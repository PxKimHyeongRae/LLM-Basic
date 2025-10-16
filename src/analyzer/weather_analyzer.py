"""
센서 데이터를 분석하여 날씨 지표를 계산하는 모듈
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


class WeatherAnalyzer:
    """날씨 데이터 분석 클래스"""

    def __init__(self, sensor_data: Dict):
        """
        Args:
            sensor_data: SensorDataFetcher에서 반환된 센서 데이터
        """
        self.sensor_data = sensor_data
        self.temperature = sensor_data.get('temperature', {})
        self.humidity = sensor_data.get('humidity', {})
        self.date = sensor_data.get('date')

    def analyze(self) -> Dict:
        """
        센서 데이터를 분석하여 주요 지표 계산

        Returns:
            dict: {
                'max_temp': 최고 온도,
                'min_temp': 최저 온도,
                'temp_diff': 일교차,
                'avg_temp': 평균 온도,
                'max_humidity': 최고 습도,
                'min_humidity': 최저 습도,
                'humidity_diff': 습도 변화폭,
                'avg_humidity': 평균 습도,
                'discomfort_index': 불쾌지수,
                'temp_category': 온도 카테고리,
                'humidity_category': 습도 카테고리,
                'temp_diff_category': 일교차 카테고리
            }
        """
        # 온도 지표
        max_temp = self.temperature.get('max', 0)
        min_temp = self.temperature.get('min', 0)
        avg_temp = self.temperature.get('avg', 0)
        temp_diff = max_temp - min_temp

        # 습도 지표
        max_humidity = self.humidity.get('max', 0)
        min_humidity = self.humidity.get('min', 0)
        avg_humidity = self.humidity.get('avg', 0)
        humidity_diff = max_humidity - min_humidity

        # 불쾌지수 계산
        discomfort_index = self._calculate_discomfort_index(avg_temp, avg_humidity)

        # 카테고리 분류
        temp_category = self._categorize_temperature(avg_temp)
        humidity_category = self._categorize_humidity(avg_humidity)
        temp_diff_category = self._categorize_temp_diff(temp_diff)

        result = {
            'max_temp': round(max_temp, 1),
            'min_temp': round(min_temp, 1),
            'temp_diff': round(temp_diff, 1),
            'avg_temp': round(avg_temp, 1),
            'max_humidity': round(max_humidity, 1),
            'min_humidity': round(min_humidity, 1),
            'humidity_diff': round(humidity_diff, 1),
            'avg_humidity': round(avg_humidity, 1),
            'discomfort_index': round(discomfort_index, 1),
            'temp_category': temp_category,
            'humidity_category': humidity_category,
            'temp_diff_category': temp_diff_category,
            'date': self.date
        }

        logger.info(f"분석 완료 - 일교차: {temp_diff:.1f}°C ({temp_diff_category}), "
                   f"평균 온도: {avg_temp:.1f}°C ({temp_category}), "
                   f"평균 습도: {avg_humidity:.1f}% ({humidity_category})")

        return result

    @staticmethod
    def _calculate_discomfort_index(temp: float, humidity: float) -> float:
        """
        불쾌지수 계산
        DI = 0.81 × 기온 + 0.01 × 습도 × (0.99 × 기온 - 14.3) + 46.3

        Args:
            temp: 온도 (°C)
            humidity: 습도 (%)

        Returns:
            float: 불쾌지수
        """
        di = 0.81 * temp + 0.01 * humidity * (0.99 * temp - 14.3) + 46.3
        return di

    @staticmethod
    def _categorize_temperature(temp: float) -> str:
        """
        온도 카테고리 분류

        Args:
            temp: 평균 온도

        Returns:
            str: 카테고리 ('한파', '추움', '선선', '적정', '더움', '폭염')
        """
        if temp < 0:
            return '한파'
        elif temp < 10:
            return '추움'
        elif temp < 15:
            return '선선'
        elif temp < 20:
            return '쾌적'
        elif temp < 28:
            return '적정'
        elif temp < 33:
            return '더움'
        else:
            return '폭염'

    @staticmethod
    def _categorize_humidity(humidity: float) -> str:
        """
        습도 카테고리 분류

        Args:
            humidity: 평균 습도

        Returns:
            str: 카테고리 ('매우 건조', '건조', '적정', '습함', '매우 습함')
        """
        if humidity < 30:
            return '매우 건조'
        elif humidity < 40:
            return '건조'
        elif humidity < 60:
            return '적정'
        elif humidity < 80:
            return '습함'
        else:
            return '매우 습함'

    @staticmethod
    def _categorize_temp_diff(temp_diff: float) -> str:
        """
        일교차 카테고리 분류

        Args:
            temp_diff: 일교차

        Returns:
            str: 카테고리 ('작음', '보통', '큼', '매우 큼')
        """
        if temp_diff < 5:
            return '작음'
        elif temp_diff < 10:
            return '보통'
        elif temp_diff < 15:
            return '큼'
        else:
            return '매우 큼'

    def get_summary_text(self) -> str:
        """
        분석 결과를 간단한 텍스트로 요약

        Returns:
            str: 요약 텍스트
        """
        analysis = self.analyze()

        summary = (
            f"온도: {analysis['min_temp']}~{analysis['max_temp']}°C "
            f"(일교차 {analysis['temp_diff']}°C), "
            f"습도: {analysis['avg_humidity']}%"
        )

        return summary

    @staticmethod
    def compare_two_days(yesterday_data: Dict, today_data: Dict) -> Dict:
        """
        어제와 오늘의 평균 온도를 비교

        Args:
            yesterday_data: 어제의 분석 데이터
            today_data: 오늘의 분석 데이터

        Returns:
            dict: {
                'yesterday_avg_temp': 어제 평균 온도,
                'today_avg_temp': 오늘 평균 온도,
                'temp_change': 온도 변화량,
                'temp_change_direction': 변화 방향 ('상승', '하강', '동일'),
                'yesterday_date': 어제 날짜,
                'today_date': 오늘 날짜,
                'yesterday_analysis': 어제 전체 분석 데이터,
                'today_analysis': 오늘 전체 분석 데이터
            }
        """
        yesterday_avg = yesterday_data['avg_temp']
        today_avg = today_data['avg_temp']
        temp_change = today_avg - yesterday_avg

        if temp_change > 0:
            direction = '상승'
        elif temp_change < 0:
            direction = '하강'
        else:
            direction = '동일'

        result = {
            'yesterday_avg_temp': yesterday_avg,
            'today_avg_temp': today_avg,
            'temp_change': round(temp_change, 1),
            'temp_change_direction': direction,
            'yesterday_date': yesterday_data.get('date'),
            'today_date': today_data.get('date'),
            'yesterday_analysis': yesterday_data,
            'today_analysis': today_data
        }

        logger.info(f"온도 비교 - 어제: {yesterday_avg:.1f}°C, "
                   f"오늘: {today_avg:.1f}°C, "
                   f"변화: {temp_change:+.1f}°C ({direction})")

        return result
