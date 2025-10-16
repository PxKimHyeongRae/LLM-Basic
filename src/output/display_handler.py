"""
전광판 출력 및 로깅 처리 모듈
"""

import json
import os
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class DisplayHandler:
    """전광판 출력 및 로깅 처리 클래스"""

    def __init__(self, log_dir: str = './data/logs'):
        """
        Args:
            log_dir: 로그 파일을 저장할 디렉토리
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def send_to_display(self, message: str):
        """
        전광판에 문구 전송 (구현 필요)

        Args:
            message: 전송할 문구
        """
        # TODO: 실제 전광판 API/시스템과 연동
        # 현재는 콘솔 출력으로 대체
        print("\n" + "=" * 70)
        print(f"[전광판 출력] {message}")
        print("=" * 70 + "\n")

        logger.info(f"전광판 출력: {message}")

    def log_message(
        self,
        date: datetime,
        message: str,
        analysis_data: Dict,
        log_type: str = "daily"
    ):
        """
        생성된 문구와 분석 데이터를 로그 파일에 저장

        Args:
            date: 날짜
            message: 생성된 문구
            analysis_data: 분석 데이터
            log_type: 로그 타입 ('daily', 'monthly')
        """
        # 로그 파일명 생성
        if log_type == "daily":
            log_filename = f"display_messages_{date.strftime('%Y%m')}.jsonl"
        else:
            log_filename = f"display_messages_{date.strftime('%Y')}.jsonl"

        log_filepath = os.path.join(self.log_dir, log_filename)

        # 로그 데이터 구성
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
            'message': message,
            'analysis': {
                'max_temp': analysis_data.get('max_temp'),
                'min_temp': analysis_data.get('min_temp'),
                'temp_diff': analysis_data.get('temp_diff'),
                'avg_temp': analysis_data.get('avg_temp'),
                'avg_humidity': analysis_data.get('avg_humidity'),
                'temp_category': analysis_data.get('temp_category'),
                'humidity_category': analysis_data.get('humidity_category'),
                'temp_diff_category': analysis_data.get('temp_diff_category')
            }
        }

        # JSONL 형식으로 저장 (한 줄에 하나의 JSON)
        try:
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            logger.info(f"로그 저장 완료: {log_filepath}")
        except Exception as e:
            logger.error(f"로그 저장 실패: {e}")

    def get_message_history(self, year: int, month: int) -> list:
        """
        특정 월의 메시지 히스토리 조회

        Args:
            year: 연도
            month: 월

        Returns:
            list: 메시지 히스토리 (딕셔너리 리스트)
        """
        log_filename = f"display_messages_{year:04d}{month:02d}.jsonl"
        log_filepath = os.path.join(self.log_dir, log_filename)

        if not os.path.exists(log_filepath):
            logger.warning(f"로그 파일이 존재하지 않습니다: {log_filepath}")
            return []

        history = []
        try:
            with open(log_filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    history.append(json.loads(line.strip()))
        except Exception as e:
            logger.error(f"로그 파일 읽기 실패: {e}")

        return history

    def export_to_text(self, message: str, analysis_data: Dict, output_file: str = None):
        """
        문구를 텍스트 파일로 출력 (전광판 시스템이 텍스트 파일을 읽는 경우)

        Args:
            message: 전송할 문구
            analysis_data: 분석 데이터
            output_file: 출력 파일 경로 (기본값: ./data/current_message.txt)
        """
        if output_file is None:
            output_file = './data/current_message.txt'

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"{message}\n")
                f.write(f"\n")
                f.write(f"온도: {analysis_data['min_temp']}~{analysis_data['max_temp']}°C\n")
                f.write(f"일교차: {analysis_data['temp_diff']}°C\n")
                f.write(f"습도: {analysis_data['avg_humidity']}%\n")

            logger.info(f"텍스트 파일 출력 완료: {output_file}")
        except Exception as e:
            logger.error(f"텍스트 파일 출력 실패: {e}")
