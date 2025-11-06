"""
전광판 메시지 출력 후처리 모듈
모델의 출력에서 불필요한 내용을 제거하고 깔끔하게 정리합니다.
"""

import re
from typing import Optional


def clean_output(text: str, max_length: int = 70) -> str:
    """
    모델 출력을 전광판 메시지로 정리합니다.

    제거 대상:
    - 특수 토큰 (<think>, </think> 등)
    - 질문 형식
    - 메타 설명 ("전광판에 표시할 메시지:", "답변:" 등)
    - 이모지 (선택적)
    - 과도한 공백
    - 불필요한 줄바꿈

    Args:
        text: 원본 텍스트
        max_length: 최대 길이 (기본 70자)

    Returns:
        정리된 텍스트
    """
    if not text:
        return ""

    original = text

    # 1. 특수 토큰 제거 (<think>, <|im_start|> 등)
    text = re.sub(r'<[^>]+>', '', text)

    # 2. 메타 설명 제거
    meta_patterns = [
        r'^전광판에 표시할 메시지:\s*',
        r'^출력:\s*',
        r'^답변:\s*',
        r'^메시지:\s*',
        r'^\s*\n',
    ]
    for pattern in meta_patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)

    # 3. 질문 부분 제거 (물음표 이후)
    # "이 메시지가 적절한가요?" 같은 것 제거
    if '?' in text:
        sentences = text.split('.')
        cleaned_sentences = []
        for sentence in sentences:
            if '?' not in sentence:
                cleaned_sentences.append(sentence)
            else:
                # 물음표 앞까지만 유지
                before_question = sentence.split('?')[0]
                if before_question.strip() and len(before_question.strip()) > 10:
                    cleaned_sentences.append(before_question)
                break  # 질문이 나오면 이후는 버림
        text = '.'.join(cleaned_sentences)

    # 4. 따옴표 제거
    text = text.replace('"', '').replace('"', '').replace('"', '')
    text = text.replace("'", "").replace("'", "").replace("'", "")

    # 5. 줄바꿈을 공백으로 변환
    text = text.replace('\n', ' ')

    # 6. 과도한 공백 제거
    text = re.sub(r'\s+', ' ', text)

    # 7. 첫 번째 완결된 문장만 추출 (온전한 의미 단위)
    # 마침표, 느낌표, 물음표로 끝나는 첫 문장
    sentences = re.split(r'([.!?])', text)
    if len(sentences) >= 2:
        # 문장 + 마침표 조합
        first_sentence = sentences[0] + sentences[1]
        text = first_sentence.strip()
    else:
        text = text.strip()

    # 8. 시작 부분 정리 (불필요한 접속사 제거)
    text = re.sub(r'^(그래서|따라서|또한|또|그리고)\s+', '', text)

    # 9. 길이 제한
    if len(text) > max_length:
        # 70자를 넘으면 잘라내되, 마지막 완결 단어까지만
        text = text[:max_length-3].strip()
        # 마지막 공백이나 마침표 찾기
        last_space = text.rfind(' ')
        if last_space > max_length * 0.8:  # 80% 이상이면 단어 경계에서 자름
            text = text[:last_space]
        text = text.rstrip('.,!?') + '...'

    # 10. 마침표 확인
    if text and not text[-1] in '.!?':
        text += '.'

    # 11. 최종 검증 - 너무 짧거나 의미 없는 경우 원본 반환
    if len(text.strip()) < 10:
        # 원본에서 첫 70자만 반환
        return original[:max_length].strip()

    return text.strip()


def extract_temperature_comparison(text: str) -> Optional[dict]:
    """
    텍스트에서 온도 비교 정보를 추출합니다.

    Args:
        text: 분석할 텍스트

    Returns:
        온도 차이 정보 또는 None
    """
    # "10도 상승", "5도 하강", "20도 따뜻", "15도 추움" 등
    patterns = [
        r'(\d+)도\s*(상승|올라|따뜻|높아)',
        r'(\d+)도\s*(하강|내려|추워|낮아)',
        r'어제보다\s*(\d+)도',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            temp_diff = int(match.group(1))
            if '하강' in text or '내려' in text or '추워' in text or '낮아' in text:
                temp_diff = -temp_diff
            return {
                'diff': temp_diff,
                'mentioned': True
            }

    return None


def validate_output(text: str) -> dict:
    """
    출력 품질을 검증합니다.

    Returns:
        검증 결과 딕셔너리
    """
    checks = {
        'length_ok': 40 <= len(text) <= 70,
        'has_period': text.endswith(('.', '!', '?')),
        'no_special_tokens': '<' not in text and '>' not in text,
        'no_questions': '?' not in text or text.count('?') == 0,
        'has_content': len(text.strip()) > 10,
    }

    checks['overall'] = all(checks.values())

    return checks


# 테스트용
if __name__ == "__main__":
    test_cases = [
        ".\n전광판에 표시할 메시지:\n\n안녕하세요, 오늘 공원은 더 시원합니다. 외출 시 가벼운 겉옷을 챙기세요. 감사합니다. 2월 5일 (화요일) 오전 9시 38분\n</think>\n\n오늘 공원",
        ".\n전광판에 표시할 메시지: \"오늘은 따뜻해졌어요! 공원에 오셔서 산책을 즐기세요.\"\n\n이 메시지가 적절한가요? 아니면 더 나은 제안이 있나요?",
        ".\n전광판에 표시할 메시지:\n\n오늘 공원은 매우 추워요, 따뜻한 옷을 입고 오세요. 난방이 되지 않는 야외 공간이므로 외출 시 주의가 필요합니다.",
        ".\n전광판에 표시할 메시지:\n\n안녕하세요, 오늘은 평균기온이 어제보다 10도나 상승해 매우 덥습니다. 물을 충분히 마시고, 햇빛에 장시간 노출되지 않도록 주의하시기 바랍니다. 감사합니다.",
    ]

    print("=" * 80)
    print("출력 정리 테스트")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        print(f"\n[테스트 {i}]")
        print(f"원본 ({len(test)}자):")
        print(f"  {test[:100]}...")

        cleaned = clean_output(test)
        print(f"\n정리 ({len(cleaned)}자):")
        print(f"  {cleaned}")

        validation = validate_output(cleaned)
        print(f"\n검증: {validation}")
        print("-" * 80)
