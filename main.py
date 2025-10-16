"""
IoT 센서 데이터 기반 전광판 문구 생성 시스템 - 메인 실행 파일
"""

import os
import sys
from datetime import date, datetime, timedelta
import logging
import argparse
import time

# 프로젝트 경로를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import DatabaseConnection
from src.analyzer.sensor_data_fetcher import SensorDataFetcher
from src.analyzer.weather_analyzer import WeatherAnalyzer
from src.generator.llm_generator import MessageGenerator
from src.generator.llm_generator_local_api import MessageGeneratorLocalAPI
from src.output.display_handler import DisplayHandler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./data/logs/system.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main(target_date=None, device_ids=None, generate_multiple=False, compare_with_yesterday=True):
    """
    메인 실행 함수

    Args:
        target_date: 조회할 날짜 (기본값: 2025년 4월 10일)
        device_ids: 디바이스 ID 리스트 (기본값: 전체)
        generate_multiple: 여러 개의 문구 생성 여부
        compare_with_yesterday: 어제와 비교할지 여부 (기본값: True)
    """
    # 전체 실행 시간 측정 시작
    start_time = time.time()

    logger.info("=" * 70)
    logger.info("IoT 센서 데이터 기반 전광판 문구 생성 시스템 시작")
    logger.info("=" * 70)

    # 날짜 설정
    if target_date is None:
        # 기본값: 2025년 4월 10일
        target_date = date(2025, 4, 10)

    yesterday_date = target_date - timedelta(days=1)

    logger.info(f"대상 날짜: {target_date} (오늘)")
    if compare_with_yesterday:
        logger.info(f"비교 날짜: {yesterday_date} (어제)")

    try:
        # 1. 데이터베이스 연결
        logger.info("\n[1단계] 데이터베이스 연결 중...")
        with DatabaseConnection() as db:
            # 연결 테스트
            if db.test_connection():
                logger.info("✓ 데이터베이스 연결 성공")
            else:
                logger.error("✗ 데이터베이스 연결 실패")
                return

            # 2. 센서 데이터 조회
            logger.info("\n[2단계] 센서 데이터 조회 중...")
            step_start = time.time()
            fetcher = SensorDataFetcher(db)

            # 사용 가능한 디바이스 확인
            if device_ids is None:
                available_devices = fetcher.get_available_devices(target_date)
                logger.info(f"사용 가능한 디바이스:")
                logger.info(f"  - 온도 센서: {', '.join(available_devices['temperature'])}")
                logger.info(f"  - 습도 센서: {', '.join(available_devices['humidity'])}")

            # 오늘 데이터 조회
            today_sensor_data = fetcher.get_daily_statistics(
                target_date=target_date,
                device_ids=device_ids
            )

            # 데이터 확인
            if not today_sensor_data['temperature']['hourly_data']:
                logger.warning("⚠️  오늘 온도 데이터가 없습니다.")
                return

            # 어제 데이터 조회 (비교 모드인 경우)
            yesterday_sensor_data = None
            if compare_with_yesterday:
                yesterday_sensor_data = fetcher.get_daily_statistics(
                    target_date=yesterday_date,
                    device_ids=device_ids
                )
                if not yesterday_sensor_data['temperature']['hourly_data']:
                    logger.warning("⚠️  어제 온도 데이터가 없습니다. 비교 모드를 해제합니다.")
                    compare_with_yesterday = False

            step_elapsed = time.time() - step_start
            logger.info(f"✓ 데이터 조회 완료 (소요 시간: {step_elapsed:.2f}초)")

            # 3. 데이터 분석
            logger.info("\n[3단계] 데이터 분석 중...")
            step_start = time.time()

            today_analyzer = WeatherAnalyzer(today_sensor_data)
            today_analysis = today_analyzer.analyze()

            logger.info(f"오늘 분석 결과:")
            logger.info(f"  - 최저 온도: {today_analysis['min_temp']}°C")
            logger.info(f"  - 최고 온도: {today_analysis['max_temp']}°C")
            logger.info(f"  - 평균 온도: {today_analysis['avg_temp']}°C")
            logger.info(f"  - 일교차: {today_analysis['temp_diff']}°C ({today_analysis['temp_diff_category']})")
            logger.info(f"  - 평균 습도: {today_analysis['avg_humidity']}% ({today_analysis['humidity_category']})")

            # 어제와 비교 (비교 모드인 경우)
            comparison_result = None
            if compare_with_yesterday and yesterday_sensor_data:
                yesterday_analyzer = WeatherAnalyzer(yesterday_sensor_data)
                yesterday_analysis = yesterday_analyzer.analyze()

                logger.info(f"\n어제 분석 결과:")
                logger.info(f"  - 평균 온도: {yesterday_analysis['avg_temp']}°C")

                comparison_result = WeatherAnalyzer.compare_two_days(yesterday_analysis, today_analysis)

            step_elapsed = time.time() - step_start
            logger.info(f"✓ 데이터 분석 완료 (소요 시간: {step_elapsed:.2f}초)")

            # 4. LLM 문구 생성
            logger.info("\n[4단계] LLM 문구 생성 중...")
            step_start = time.time()

            # API 모드 확인 (환경변수로 제어)
            use_api_mode = os.getenv('USE_MODEL_SERVER', 'true').lower() == 'true'

            if use_api_mode:
                logger.info("모드: 로컬 모델 서버 API 사용")
                generator = MessageGeneratorLocalAPI()
            else:
                logger.info("모드: 직접 모델 로드")
                generator = MessageGenerator()

            if comparison_result:
                # 어제와 오늘 비교 문구 생성
                message = generator.generate_comparison_message(comparison_result)
            elif generate_multiple:
                # 여러 개의 문구 생성
                messages = generator.generate_multiple_messages(today_analysis, num_messages=3)
                logger.info(f"\n생성된 문구들:")
                for i, msg in enumerate(messages, 1):
                    logger.info(f"  {i}. {msg}")

                # 첫 번째 문구 사용
                message = messages[0]
            else:
                # 단일 문구 생성
                message = generator.generate_message(today_analysis)

            step_elapsed = time.time() - step_start
            logger.info(f"✓ 문구 생성 완료 (소요 시간: {step_elapsed:.2f}초)")

            # 5. 출력 및 로깅
            logger.info("\n[5단계] 출력 및 로깅...")
            step_start = time.time()
            display = DisplayHandler()
            display.send_to_display(message)

            # 비교 결과가 있으면 비교 정보도 함께 로깅
            if comparison_result:
                display.log_message(target_date, message, today_analysis)
                display.export_to_text(message, today_analysis)
            else:
                display.log_message(target_date, message, today_analysis)
                display.export_to_text(message, today_analysis)

            step_elapsed = time.time() - step_start
            logger.info(f"✓ 출력 및 로깅 완료 (소요 시간: {step_elapsed:.2f}초)")

            # 전체 실행 시간 계산
            total_elapsed = time.time() - start_time
            logger.info("\n" + "=" * 70)
            logger.info(f"✓ 모든 작업 완료")
            logger.info(f"총 실행 시간: {total_elapsed:.2f}초")
            logger.info("=" * 70)

    except KeyboardInterrupt:
        logger.info("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"\n오류 발생: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description='IoT 센서 데이터 기반 전광판 문구 생성')
    parser.add_argument(
        '--date',
        type=str,
        help='조회할 날짜 (YYYY-MM-DD 형식, 기본값: 어제)'
    )
    parser.add_argument(
        '--devices',
        type=str,
        nargs='+',
        help='사용할 디바이스 ID 리스트 (기본값: 전체)'
    )
    parser.add_argument(
        '--multiple',
        action='store_true',
        help='여러 개의 문구 생성'
    )
    parser.add_argument(
        '--no-compare',
        action='store_true',
        help='어제와 비교하지 않음 (기본값: 비교함)'
    )

    args = parser.parse_args()

    # 날짜 파싱
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"오류: 잘못된 날짜 형식입니다. YYYY-MM-DD 형식을 사용하세요.")
            sys.exit(1)

    # 실행
    main(
        target_date=target_date,
        device_ids=args.devices,
        generate_multiple=args.multiple,
        compare_with_yesterday=not args.no_compare
    )
