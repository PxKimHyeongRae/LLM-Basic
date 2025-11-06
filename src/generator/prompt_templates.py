"""
LLM 프롬프트 템플릿 관리
"""


class PromptTemplates:
    """프롬프트 템플릿 관리 클래스"""

    @staticmethod
    def get_display_message_prompt(analysis_data: dict) -> str:
        """
        전광판 문구 생성을 위한 프롬프트 생성

        Args:
            analysis_data: WeatherAnalyzer.analyze()의 결과

        Returns:
            str: LLM에 전달할 프롬프트
        """
        prompt = f"""당신은 시민들에게 친근하게 날씨 정보를 전달하는 전광판 문구 작성자입니다.

오늘의 날씨 데이터:
- 최고 온도: {analysis_data['max_temp']}°C
- 최저 온도: {analysis_data['min_temp']}°C
- 일교차: {analysis_data['temp_diff']}°C ({analysis_data['temp_diff_category']})
- 평균 온도: {analysis_data['avg_temp']}°C ({analysis_data['temp_category']})
- 평균 습도: {analysis_data['avg_humidity']}% ({analysis_data['humidity_category']})
- 불쾌지수: {analysis_data['discomfort_index']}

위 데이터를 바탕으로 시민들에게 유용한 조언을 담은 한 문장의 전광판 문구를 작성해주세요.
문구는 50자 이내로 친근하고 따뜻한 톤으로 작성해주세요.

전광판 문구:"""

        return prompt

    @staticmethod
    def get_display_message_prompt_with_examples(analysis_data: dict) -> str:
        """
        Few-shot 예시를 포함한 프롬프트 생성

        Args:
            analysis_data: WeatherAnalyzer.analyze()의 결과

        Returns:
            str: LLM에 전달할 프롬프트
        """
        temp_diff = analysis_data['temp_diff']
        avg_temp = analysis_data['avg_temp']
        avg_humidity = analysis_data['avg_humidity']

        prompt = f"""당신은 시민들에게 친근하게 날씨 정보를 전달하는 전광판 문구 작성자입니다.

다음은 좋은 전광판 문구의 예시입니다:

예시 1:
- 일교차: 12°C, 평균 온도: 18°C, 습도: 55%
- 문구: "오늘 일교차가 12도로 큽니다. 외출 시 겉옷을 챙기세요!"

예시 2:
- 일교차: 7°C, 평균 온도: 28°C, 습도: 75%
- 문구: "더운 날씨가 계속됩니다. 충분한 수분 섭취하세요!"

예시 3:
- 일교차: 5°C, 평균 온도: 8°C, 습도: 35%
- 문구: "쌀쌀한 날씨입니다. 따뜻하게 입고 외출하세요."

예시 4:
- 일교차: 15°C, 평균 온도: 15°C, 습도: 45%
- 문구: "일교차가 15도로 매우 큽니다. 건강 관리 유의하세요!"

이제 오늘의 날씨 데이터를 바탕으로 문구를 작성해주세요:
- 최고 온도: {analysis_data['max_temp']}°C
- 최저 온도: {analysis_data['min_temp']}°C
- 일교차: {temp_diff}°C
- 평균 온도: {avg_temp}°C
- 평균 습도: {avg_humidity}%

위 데이터를 바탕으로 시민들에게 유용한 조언을 담은 한 문장의 전광판 문구를 작성해주세요.
문구는 50자 이내로 친근하고 따뜻한 톤으로 작성해주세요. 예시와 비슷한 스타일로 작성하되, 동일한 문구는 피해주세요.

전광판 문구:"""

        return prompt

    @staticmethod
    def get_simple_instruction_prompt(analysis_data: dict) -> str:
        """
        간단한 지시형 프롬프트 (더 직접적)

        Args:
            analysis_data: WeatherAnalyzer.analyze()의 결과

        Returns:
            str: LLM에 전달할 프롬프트
        """
        temp_diff = analysis_data['temp_diff']
        avg_temp = analysis_data['avg_temp']

        # 핵심 조건 판단
        advice = ""
        if temp_diff >= 10:
            advice = "일교차가 큰 날씨"
        elif avg_temp >= 28:
            advice = "더운 날씨"
        elif avg_temp < 10:
            advice = "추운 날씨"
        else:
            advice = "쾌적한 날씨"

        prompt = f"""오늘은 {advice}입니다.
최저 {analysis_data['min_temp']}°C, 최고 {analysis_data['max_temp']}°C, 일교차 {temp_diff}°C입니다.

시민들에게 짧고 친근한 한 문장으로 조언해주세요 (50자 이내):"""

        return prompt

    @staticmethod
    def get_temperature_comparison_prompt(comparison_data: dict) -> str:
        """
        어제와 오늘의 평균 온도 비교를 위한 프롬프트 (개선 버전)

        Args:
            comparison_data: WeatherAnalyzer.compare_two_days()의 결과

        Returns:
            str: LLM에 전달할 프롬프트
        """
        yesterday_avg = comparison_data['yesterday_avg_temp']
        today_avg = comparison_data['today_avg_temp']
        temp_change = comparison_data['temp_change']
        direction = comparison_data['temp_change_direction']

        prompt = f"""<instruction>
당신은 공원 전광판 메시지 전문가입니다. 주어진 온도 데이터를 간결한 한 문장으로 변환하세요.
</instruction>

<rules>
1. 반드시 한 문장만 출력하세요
2. 마크다운(**, ---, #), 특수문자, 이모지 사용 금지
3. 괄호나 설명 추가 금지
4. 질문 형식 금지
5. "출력:", "답:", "메시지:" 같은 레이블 없이 메시지만 작성
6. 40-70자 길이로 작성
7. 온도 차이를 구체적 숫자로 명시 (예: "5도", "10도")
</rules>

<bad_examples>
❌ "---\n**전광판 메시지:**\n오늘 공원은..."
❌ "오늘은 춥습니다. (또는) 따뜻하게 입고..."
❌ "오늘은 추워요. 어떻게 생각하시나요?"
❌ "출력: 오늘은 춥습니다..."
</bad_examples>

<good_examples>
입력: 어제 20도, 오늘 30도
출력: 어제보다 10도 올라 무더워졌습니다. 수분을 충분히 섭취하세요.

입력: 어제 10도, 오늘 -10도
출력: 어제보다 20도 급격히 내려갔습니다. 방한 준비 철저히 하세요.

입력: 어제 15도, 오늘 16도
출력: 어제와 비슷한 날씨입니다. 산책하기 좋은 하루예요.

입력: 어제 25도, 오늘 15도
출력: 어제보다 10도 낮아졌습니다. 외출 시 겉옷 챙기세요.

입력: 어제 5도, 오늘 8도
출력: 어제보다 3도 올라 조금 포근해졌습니다. 좋은 하루 되세요.

입력: 어제 18도, 오늘 12도
출력: 어제보다 6도 내려가 쌀쌀합니다. 따뜻하게 입으세요.
</good_examples>

<task>
입력: 어제 {yesterday_avg:.0f}도, 오늘 {today_avg:.0f}도
출력:"""

        return prompt

    @staticmethod
    def get_temperature_chat_prompt(yesterday_temp: float, today_temp: float) -> str:
        """
        Chat 형식의 온도 비교 프롬프트
        파인튜닝 데이터와 동일한 형식 사용

        Args:
            yesterday_temp: 어제 평균 온도
            today_temp: 오늘 평균 온도

        Returns:
            str: Chat 형식 프롬프트
        """
        system_prompt = "당신은 공원 전광판 메시지 전문가입니다. 온도 정보를 받아 40-70자 길이의 간결한 한 문장 메시지를 작성하세요. 온도 차이를 구체적 숫자로 명시하고 공원 관련 조언을 포함하세요."

        prompt = f"""<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
어제 {yesterday_temp:.0f}도, 오늘 {today_temp:.0f}도<|im_end|>
<|im_start|>assistant
"""

        return prompt
