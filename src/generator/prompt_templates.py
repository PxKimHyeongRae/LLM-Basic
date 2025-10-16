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
        어제와 오늘의 평균 온도 비교를 위한 프롬프트

        Args:
            comparison_data: WeatherAnalyzer.compare_two_days()의 결과

        Returns:
            str: LLM에 전달할 프롬프트
        """
        yesterday_avg = comparison_data['yesterday_avg_temp']
        today_avg = comparison_data['today_avg_temp']
        temp_change = comparison_data['temp_change']
        direction = comparison_data['temp_change_direction']

        today_data = comparison_data['today_analysis']

        # 온도 변화에 따른 조언 힌트
        if abs(temp_change) < 1:
            advice_hint = "어제와 비슷한 날씨"
        elif direction == '상승':
            if temp_change >= 5:
                advice_hint = "어제보다 많이 따뜻함, 얇게 입기"
            else:
                advice_hint = "어제보다 약간 따뜻함"
        else:  # 하강
            if abs(temp_change) >= 5:
                advice_hint = "어제보다 많이 추움, 따뜻하게 입기"
            else:
                advice_hint = "어제보다 약간 선선함"

        # 일교차 조언
        if today_data['temp_diff'] >= 15:
            diff_advice = "일교차가 매우 크니 겉옷 필수"
        elif today_data['temp_diff'] >= 10:
            diff_advice = "일교차가 크니 겉옷 챙기기"
        else:
            diff_advice = ""

        prompt = f"""전광판에 표시할 날씨 안내 문구를 한 문장으로 작성하세요.

날씨 정보:
- 어제 평균: {yesterday_avg:.1f}°C → 오늘 평균: {today_avg:.1f}°C ({temp_change:+.1f}°C {direction})
- 오늘 최저/최고: {today_data['min_temp']}°C / {today_data['max_temp']}°C
- 조언: {advice_hint}{', ' + diff_advice if diff_advice else ''}

위 정보를 바탕으로 시민들에게 친근하게 날씨를 알리는 한 문장을 작성하세요. (50자 이내)

문구:"""

        return prompt
