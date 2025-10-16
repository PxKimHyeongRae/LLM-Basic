"""
tb_sensor_statistics 테이블에서 센서 데이터를 조회하는 모듈
"""

from datetime import date, datetime
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class SensorDataFetcher:
    """센서 통계 데이터 조회 클래스"""

    def __init__(self, db_connection):
        """
        Args:
            db_connection: DatabaseConnection 인스턴스
        """
        self.db = db_connection

    def get_daily_statistics(
        self,
        target_date: date,
        device_ids: Optional[List[str]] = None,
        object_id: Optional[str] = None
    ) -> Dict:
        """
        특정 날짜의 온도/습도 통계 데이터 조회

        Args:
            target_date: 조회할 날짜
            device_ids: 디바이스 ID 리스트 (None이면 전체)
            object_id: 객체 ID (특정 위치/그룹 필터링)

        Returns:
            dict: {
                'temperature': {
                    'hourly_data': [...],
                    'max': float,
                    'min': float,
                    'avg': float
                },
                'humidity': {
                    'hourly_data': [...],
                    'max': float,
                    'min': float,
                    'avg': float
                }
            }
        """
        logger.info(f"센서 데이터 조회: {target_date}")

        # 날짜를 문자열로 변환
        date_str = target_date.strftime('%Y-%m-%d')

        # 온도 데이터 조회
        temperature_data = self._get_field_statistics(
            date_str, 'Temperature', device_ids, object_id
        )

        # 습도 데이터 조회
        humidity_data = self._get_field_statistics(
            date_str, 'Humidity', device_ids, object_id
        )

        result = {
            'temperature': temperature_data,
            'humidity': humidity_data,
            'date': target_date
        }

        logger.info(f"온도 - 최소: {temperature_data['min']:.1f}°C, "
                   f"최대: {temperature_data['max']:.1f}°C, "
                   f"평균: {temperature_data['avg']:.1f}°C")
        logger.info(f"습도 - 최소: {humidity_data['min']:.1f}%, "
                   f"최대: {humidity_data['max']:.1f}%, "
                   f"평균: {humidity_data['avg']:.1f}%")

        return result

    def _get_field_statistics(
        self,
        date_str: str,
        field_key: str,
        device_ids: Optional[List[str]] = None,
        object_id: Optional[str] = None
    ) -> Dict:
        """
        특정 field_key의 통계 데이터 조회

        Args:
            date_str: 날짜 문자열 (YYYY-MM-DD)
            field_key: 'Temperature' 또는 'Humidity'
            device_ids: 디바이스 ID 리스트
            object_id: 객체 ID

        Returns:
            dict: {'hourly_data': [...], 'max': float, 'min': float, 'avg': float}
        """
        # WHERE 조건 구성
        where_conditions = [
            "statistics_date = %(date)s",
            "field_key = %(field_key)s",
            "period_type = 'HOURLY'"
        ]
        params = {
            'date': date_str,
            'field_key': field_key
        }

        if device_ids:
            placeholders = ', '.join([f"%(device_{i})s" for i in range(len(device_ids))])
            where_conditions.append(f"device_id IN ({placeholders})")
            for i, device_id in enumerate(device_ids):
                params[f'device_{i}'] = device_id

        if object_id:
            where_conditions.append("object_id = %(object_id)s")
            params['object_id'] = object_id

        where_clause = " AND ".join(where_conditions)

        # 시간별 데이터 조회
        hourly_query = f"""
            SELECT
                hour,
                AVG(avg_value) as avg_value,
                MAX(max_value) as max_value,
                MIN(min_value) as min_value,
                SUM(count) as total_count
            FROM tb_sensor_statistics
            WHERE {where_clause}
            GROUP BY hour
            ORDER BY hour
        """

        hourly_data = self.db.execute_query(hourly_query, params)

        # 일일 전체 통계 조회
        daily_query = f"""
            SELECT
                MAX(max_value) as daily_max,
                MIN(min_value) as daily_min,
                AVG(avg_value) as daily_avg
            FROM tb_sensor_statistics
            WHERE {where_clause}
        """

        daily_stats = self.db.execute_one(daily_query, params)

        if not daily_stats or daily_stats['daily_max'] is None:
            logger.warning(f"{field_key} 데이터가 없습니다: {date_str}")
            return {
                'hourly_data': [],
                'max': 0.0,
                'min': 0.0,
                'avg': 0.0
            }

        return {
            'hourly_data': hourly_data,
            'max': float(daily_stats['daily_max']),
            'min': float(daily_stats['daily_min']),
            'avg': float(daily_stats['daily_avg'])
        }

    def get_available_devices(self, target_date: date) -> Dict[str, List[str]]:
        """
        특정 날짜에 데이터가 있는 디바이스 목록 조회

        Args:
            target_date: 조회할 날짜

        Returns:
            dict: {'temperature': [...], 'humidity': [...]}
        """
        date_str = target_date.strftime('%Y-%m-%d')

        query = """
            SELECT DISTINCT device_id, field_key
            FROM tb_sensor_statistics
            WHERE statistics_date = %(date)s
              AND period_type = 'HOURLY'
            ORDER BY field_key, device_id
        """

        results = self.db.execute_query(query, {'date': date_str})

        devices = {
            'temperature': [],
            'humidity': []
        }

        for row in results:
            if row['field_key'] == 'Temperature':
                devices['temperature'].append(row['device_id'])
            elif row['field_key'] == 'Humidity':
                devices['humidity'].append(row['device_id'])

        return devices
