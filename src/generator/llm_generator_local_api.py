"""
로컬 모델 서버 API를 사용한 문구 생성 모듈
model_server.py가 실행 중이어야 합니다.
"""

import os
from dotenv import load_dotenv
import requests
from typing import Dict, Optional
import logging
import re

from .prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)
load_dotenv()


class MessageGeneratorLocalAPI:
    """로컬 모델 서버 API 기반 전광판 문구 생성 클래스"""

    def __init__(
        self,
        server_url: Optional[str] = None,
        timeout: int = 120
    ):
        """
        Args:
            server_url: 모델 서버 URL (기본값: 환경변수 또는 http://localhost:8000)
            timeout: API 타임아웃 (초)
        """
        self.server_url = server_url or os.getenv(
            'MODEL_SERVER_URL',
            'http://localhost:8000'
        )
        self.timeout = timeout
        self.generate_url = f"{self.server_url}/generate"
        self.health_url = f"{self.server_url}/health"

        logger.info(f"로컬 API 모드로 초기화: {self.server_url}")

        # 서버 상태 확인
        if not self.check_server_health():
            logger.warning("⚠️  모델 서버가 실행 중이 아닙니다!")
            logger.warning(f"다음 명령으로 서버를 시작하세요: python model_server.py")

    def check_server_health(self) -> bool:
        """서버 상태 확인"""
        try:
            response = requests.get(self.health_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('model_loaded'):
                    logger.info("✓ 모델 서버 연결 성공 (모델 로드 완료)")
                    return True
                else:
                    logger.warning("⚠️  모델 서버 연결됨 (모델 로딩 중...)")
                    return False
            else:
                logger.warning(f"서버 응답 오류: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.warning("서버 연결 실패: 서버가 실행 중이 아닙니다.")
            return False
        except Exception as e:
            logger.warning(f"서버 상태 확인 실패: {e}")
            return False

    def _query_api(
        self,
        prompt: str,
        max_new_tokens: int = 50,
        temperature: float = 0.5,
        top_p: float = 0.85,
        repetition_penalty: float = 1.2
    ) -> Optional[str]:
        """
        로컬 모델 서버 API로 텍스트 생성

        Args:
            prompt: 입력 프롬프트
            max_new_tokens: 최대 생성 토큰 수
            temperature: 생성 다양성
            top_p: Nucleus sampling
            repetition_penalty: 반복 방지 패널티

        Returns:
            str: 생성된 텍스트 (실패 시 None)
        """
        payload = {
            "prompt": prompt,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "repetition_penalty": repetition_penalty,
            "do_sample": True
        }

        try:
            logger.debug(f"API 요청: {self.generate_url}")
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('generated_text', '')
                generation_time = result.get('generation_time', 0)
                logger.info(f"✓ API 생성 성공 (소요 시간: {generation_time:.2f}초)")
                return generated_text

            elif response.status_code == 503:
                logger.warning("모델이 아직 로딩 중입니다. 잠시 후 다시 시도하세요.")
                return None

            else:
                logger.error(f"API 오류 {response.status_code}: {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"API 타임아웃 ({self.timeout}초 초과)")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("서버 연결 실패. model_server.py가 실행 중인지 확인하세요.")
            return None
        except Exception as e:
            logger.error(f"API 호출 실패: {e}")
            return None

    def generate_message(
        self,
        analysis_data: Dict,
        use_few_shot: bool = True,
        max_length: int = 50,
        temperature: float = 0.5,
        top_p: float = 0.85,
        repetition_penalty: float = 1.2
    ) -> str:
        """
        날씨 분석 데이터를 바탕으로 전광판 문구 생성

        Args:
            analysis_data: WeatherAnalyzer.analyze()의 결과
            use_few_shot: Few-shot 예시 포함 여부
            max_length: 생성할 최대 토큰 수
            temperature: 생성 다양성
            top_p: Nucleus sampling
            repetition_penalty: 반복 방지 패널티

        Returns:
            str: 생성된 전광판 문구
        """
        # 프롬프트 생성
        if use_few_shot:
            prompt = PromptTemplates.get_display_message_prompt_with_examples(analysis_data)
        else:
            prompt = PromptTemplates.get_display_message_prompt(analysis_data)

        logger.info("API를 통한 문구 생성 시작...")

        # API 호출
        full_output = self._query_api(
            prompt,
            max_new_tokens=max_length,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty
        )

        if full_output:
            # 결과 정제
            message = self._extract_message(full_output)

            # 메시지가 비어있거나 너무 짧으면 폴백 사용
            if not message or len(message) < 5:
                logger.warning(f"생성된 문구가 너무 짧음: '{message}', 폴백 사용")
                return self._get_fallback_message(analysis_data)

            logger.info(f"✓ 문구 생성 완료: {message}")
            return message
        else:
            # API 실패 시 폴백
            logger.warning("API 생성 실패, 폴백 메시지 사용")
            return self._get_fallback_message(analysis_data)

    def generate_comparison_message(
        self,
        comparison_data: Dict,
        max_length: int = 50,
        temperature: float = 0.5,
        top_p: float = 0.85,
        repetition_penalty: float = 1.2
    ) -> str:
        """
        어제와 오늘의 온도 비교 데이터를 바탕으로 전광판 문구 생성

        Args:
            comparison_data: WeatherAnalyzer.compare_two_days()의 결과
            max_length: 생성할 최대 토큰 수
            temperature: 생성 다양성
            top_p: Nucleus sampling
            repetition_penalty: 반복 방지 패널티

        Returns:
            str: 생성된 전광판 문구
        """
        # 프롬프트 생성
        prompt = PromptTemplates.get_temperature_comparison_prompt(comparison_data)

        logger.info("온도 비교 문구 생성 시작...")

        # API 호출
        full_output = self._query_api(
            prompt,
            max_new_tokens=max_length,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty
        )

        if full_output:
            # 결과 정제
            message = self._extract_message(full_output)

            # 메시지가 비어있거나 너무 짧으면 폴백 사용
            if not message or len(message) < 5:
                logger.warning(f"생성된 문구가 너무 짧음: '{message}', 폴백 사용")
                return self._get_comparison_fallback_message(comparison_data)

            logger.info(f"✓ 온도 비교 문구 생성 완료: {message}")
            return message
        else:
            # API 실패 시 폴백
            logger.warning("API 생성 실패, 폴백 메시지 사용")
            return self._get_comparison_fallback_message(comparison_data)

    def _extract_message(self, full_output: str) -> str:
        """
        생성된 텍스트에서 전광판 문구만 추출

        Args:
            full_output: API가 생성한 전체 텍스트

        Returns:
            str: 추출된 전광판 문구
        """
        # 첫 번째 문장만 추출
        sentences = re.split(r'[.!?]\s*', full_output)
        if sentences:
            message = sentences[0].strip()
        else:
            message = full_output.strip()

        # 따옴표 제거
        message = message.strip('"\'')

        # 길이 제한
        max_msg_length = int(os.getenv('MAX_MESSAGE_LENGTH', 70))
        if len(message) > max_msg_length:
            message = message[:max_msg_length]

        return message

    def _get_fallback_message(self, analysis_data: Dict) -> str:
        """
        API 실패 시 규칙 기반 폴백 메시지

        Args:
            analysis_data: 날씨 분석 데이터

        Returns:
            str: 폴백 메시지
        """
        temp_diff = analysis_data['temp_diff']
        avg_temp = analysis_data['avg_temp']
        avg_humidity = analysis_data['avg_humidity']

        # 규칙 기반 메시지 생성
        if temp_diff >= 15:
            return f"일교차가 {temp_diff:.0f}도로 매우 큽니다. 건강 관리 유의하세요!"
        elif temp_diff >= 10:
            return f"오늘 일교차가 {temp_diff:.0f}도로 큽니다. 외출 시 겉옷을 챙기세요!"
        elif avg_temp >= 33:
            return f"폭염 주의! 충분한 수분 섭취와 무리한 야외활동 자제하세요."
        elif avg_temp >= 28:
            return f"더운 날씨가 계속됩니다. 충분한 수분 섭취하세요!"
        elif avg_temp < 0:
            return f"한파 주의! 따뜻하게 입고 외출하세요."
        elif avg_temp < 10:
            return f"쌀쌀한 날씨입니다. 따뜻하게 입고 외출하세요."
        elif avg_humidity < 30:
            return f"건조한 날씨입니다. 수분 섭취와 보습에 신경 쓰세요."
        elif avg_humidity >= 80:
            return f"습한 날씨입니다. 실내 환기에 유의하세요."
        else:
            return f"오늘 최저 {analysis_data['min_temp']:.0f}°C, 최고 {analysis_data['max_temp']:.0f}°C입니다. 좋은 하루 보내세요!"

    def _get_comparison_fallback_message(self, comparison_data: Dict) -> str:
        """
        온도 비교 문구 생성 실패 시 규칙 기반 폴백 메시지

        Args:
            comparison_data: 온도 비교 데이터

        Returns:
            str: 폴백 메시지
        """
        yesterday_avg = comparison_data['yesterday_avg_temp']
        today_avg = comparison_data['today_avg_temp']
        temp_change = comparison_data['temp_change']
        direction = comparison_data['temp_change_direction']
        today_data = comparison_data['today_analysis']
        temp_diff = today_data['temp_diff']

        # 일교차가 매우 큰 경우 우선 처리
        if temp_diff >= 15:
            return f"일교차가 {temp_diff:.0f}도로 매우 큽니다. 겉옷 꼭 챙기세요!"
        elif temp_diff >= 10:
            return f"일교차 {temp_diff:.0f}도. 아침저녁으로 쌀쌀하니 겉옷 챙기세요!"

        # 온도 변화에 따른 메시지
        if abs(temp_change) < 1:
            return f"어제와 비슷한 날씨입니다. 좋은 하루 보내세요!"
        elif direction == '상승':
            if temp_change >= 5:
                return f"어제보다 {abs(temp_change):.1f}도 높아졌습니다. 가볍게 입으세요!"
            else:
                return f"어제보다 조금 따뜻합니다. 좋은 하루 되세요!"
        else:  # 하강
            if abs(temp_change) >= 5:
                return f"어제보다 {abs(temp_change):.1f}도 낮습니다. 따뜻하게 입으세요!"
            else:
                return f"어제보다 조금 선선합니다. 건강 유의하세요!"

    def generate_multiple_messages(
        self,
        analysis_data: Dict,
        num_messages: int = 3
    ) -> list:
        """
        여러 개의 문구를 생성하여 선택할 수 있도록 함

        Args:
            analysis_data: 날씨 분석 데이터
            num_messages: 생성할 문구 개수

        Returns:
            list: 생성된 문구 리스트
        """
        messages = []
        for i in range(num_messages):
            # temperature를 약간씩 조정하여 다양한 문구 생성
            temp = 0.4 + (i * 0.15)
            message = self.generate_message(
                analysis_data,
                use_few_shot=True,
                temperature=temp
            )
            messages.append(message)
            logger.info(f"문구 {i+1}/{num_messages}: {message}")

        return messages
