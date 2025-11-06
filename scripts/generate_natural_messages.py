"""
LLM을 활용해 자연스럽고 다양한 공원 전광판 메시지 생성
더 구체적이고 창의적인 표현 사용
"""

import json
import os
from anthropic import Anthropic

# Anthropic API 클라이언트
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# 공원 요소들 (다양성 증가)
PARK_ELEMENTS = [
    "나무 그늘", "잔디밭", "산책로", "꽃길", "분수대", "벤치",
    "연못", "정자", "조깅 코스", "운동 기구", "놀이터",
    "전망대", "숲길", "다리", "호수", "언덕"
]

# 활동 제안
ACTIVITIES = [
    "피크닉", "산책", "조깅", "휴식", "운동", "독서",
    "사진 촬영", "명상", "스트레칭", "가족 나들이"
]

# 다양한 어미
SENTENCE_ENDINGS = [
    "~세요", "~어떠세요?", "~좋아요", "~해보세요",
    "~권장합니다", "~추천해요", "~즐기세요", "~누려보세요"
]


def generate_natural_message(yesterday_temp, today_temp):
    """
    Claude AI를 사용해 자연스러운 메시지 생성
    """
    temp_diff = today_temp - yesterday_temp

    # 온도 변화 설명
    if temp_diff > 0:
        change_desc = f"어제보다 {abs(temp_diff)}도 올라"
    elif temp_diff < 0:
        change_desc = f"어제보다 {abs(temp_diff)}도 낮아져"
    else:
        change_desc = "어제와 비슷한 날씨로"

    # 날씨 상태
    if today_temp >= 35:
        weather = "매우 더워"
    elif today_temp >= 28:
        weather = "더워졌습니다"
    elif today_temp >= 20:
        weather = "따뜻해졌습니다"
    elif today_temp >= 10:
        weather = "선선해졌습니다"
    elif today_temp >= 0:
        weather = "쌀쌀해졌습니다"
    else:
        weather = "춥습니다"

    prompt = f"""공원 전광판에 표시할 메시지를 작성해주세요.

조건:
- 온도 변화: {change_desc} {weather}
- 반드시 온도 차이를 구체적 숫자로 명시 (예: "{abs(temp_diff)}도")
- 40-70자 길이의 한 문장
- 공원 요소를 구체적으로 언급 (예: 나무 그늘, 잔디밭, 꽃길, 분수대, 벤치 등)
- 자연스럽고 친근한 표현
- 마크다운, 특수문자 사용 금지

좋은 예시:
- "어제보다 10도 올라 포근해졌습니다. 공원 잔디밭에서 피크닉 어떠세요?"
- "어제보다 7도 낮아져 시원합니다. 나무 그늘 아래서 잠시 쉬어가세요."
- "어제보다 5도 올라 화창해졌습니다. 활짝 핀 꽃길을 따라 걸어보세요."
- "어제보다 3도 올라 따뜻합니다. 연못가 벤치에서 여유를 즐기세요."

나쁜 예시:
- "공원에서 활동하세요" (너무 일반적)
- "공원 산책하기 좋아요" (반복적)

메시지 작성 (메시지만 출력, 설명 없이):"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        temperature=0.8,  # 창의성 증가
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    message = response.content[0].text.strip()

    # 레이블 제거
    for label in ["메시지:", "출력:", "답:", "전광판:"]:
        if message.startswith(label):
            message = message[len(label):].strip()

    # 따옴표 제거
    message = message.strip('"\'')

    return message


def main():
    """
    wrap_temperature_data.py의 데이터를 자연스러운 메시지로 재생성
    """
    from wrap_temperature_data import TRAIN_DATA, VALIDATION_DATA

    print("=" * 70)
    print("자연스러운 메시지 생성 시작")
    print("=" * 70)
    print(f"\n총 {len(TRAIN_DATA)}개의 학습 데이터 재생성")
    print("Claude AI를 사용하여 더 자연스럽고 다양한 표현으로 변환\n")

    # API 키 확인
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   .env 파일에 ANTHROPIC_API_KEY를 추가하세요.")
        return

    new_train_data = []

    # 학습 데이터 재생성 (샘플만)
    print("샘플 10개 생성 중...\n")
    for i, (yesterday, today, old_message) in enumerate(TRAIN_DATA[:10]):
        print(f"[{i+1}/10] 어제 {yesterday}도, 오늘 {today}도")

        try:
            new_message = generate_natural_message(yesterday, today)
            new_train_data.append((yesterday, today, new_message))

            print(f"  기존: {old_message}")
            print(f"  신규: {new_message}")
            print()

        except Exception as e:
            print(f"  ❌ 생성 실패: {e}")
            # 실패 시 원본 사용
            new_train_data.append((yesterday, today, old_message))

    # 결과 저장
    output_file = "data/natural_messages_sample.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_train_data, f, ensure_ascii=False, indent=2)

    print("=" * 70)
    print(f"✓ 샘플 {len(new_train_data)}개 생성 완료: {output_file}")
    print("=" * 70)
    print("\n💡 결과가 만족스러우면 전체 데이터 생성을 진행하세요.")
    print("   (전체 302개 생성 시 약 15-20분 소요, API 비용 발생)")


if __name__ == "__main__":
    main()
