"""
패턴 기반으로 자연스럽고 다양한 공원 전광판 메시지 생성
API 없이 사용 가능
"""

import json
import random

# 공원 특화 장소/요소
PARK_LOCATIONS = [
    "나무 그늘 아래", "잔디밭", "산책로", "꽃길", "분수대 근처",
    "벤치", "연못가", "정자", "조깅 코스", "숲길",
    "다리 위", "언덕", "전망대", "호수가", "소나무 숲"
]

# 온도별 활동 제안
HOT_ACTIVITIES = [
    "나무 그늘 아래서 잠시 쉬어가세요",
    "분수대 근처가 시원합니다",
    "오전 일찍 산책 추천합니다",
    "실내 휴게소를 이용하세요",
    "수분 섭취 충분히 하세요",
    "양산을 준비하세요"
]

WARM_ACTIVITIES = [
    "잔디밭에서 피크닉 어떠세요?",
    "활짝 핀 꽃길을 따라 걸어보세요",
    "벤치에서 여유를 즐기세요",
    "산책로를 천천히 걸어보세요",
    "가족과 함께 나들이 즐기세요",
    "연못가에서 휴식을 취하세요",
    "조깅하기 딱 좋은 날씨예요",
    "사진 찍기 좋은 날입니다"
]

COOL_ACTIVITIES = [
    "가디건 하나 챙기세요",
    "가벼운 겉옷 준비하세요",
    "산책하며 단풍을 감상하세요",
    "따뜻한 차 한 잔 어떠세요?",
    "조깅으로 몸을 녹여보세요"
]

COLD_ACTIVITIES = [
    "따뜻하게 입고 짧은 산책 추천합니다",
    "두꺼운 옷 꼭 챙기세요",
    "방한 준비 철저히 하세요",
    "실내 활동 권장합니다",
    "따뜻한 음료 준비하세요"
]

# 날씨 표현 (온도별)
def get_weather_description(temp):
    if temp >= 35:
        return "무더워", "매우 더워"
    elif temp >= 30:
        return "더워졌습니다", "덥습니다"
    elif temp >= 25:
        return "따뜻해졌습니다", "포근합니다"
    elif temp >= 20:
        return "화창합니다", "쾌적합니다"
    elif temp >= 15:
        return "선선해졌습니다", "좋은 날씨입니다"
    elif temp >= 10:
        return "선선합니다", "시원해졌습니다"
    elif temp >= 5:
        return "쌀쌀해졌습니다", "선선합니다"
    elif temp >= 0:
        return "춥습니다", "쌀쌀합니다"
    else:
        return "매우 춥습니다", "영하입니다"


def get_activity_suggestion(today_temp, temp_diff):
    """온도와 변화에 따른 활동 제안"""
    if today_temp >= 30:
        return random.choice(HOT_ACTIVITIES)
    elif today_temp >= 15:
        return random.choice(WARM_ACTIVITIES)
    elif today_temp >= 5:
        return random.choice(COOL_ACTIVITIES)
    else:
        return random.choice(COLD_ACTIVITIES)


def generate_natural_message(yesterday_temp, today_temp):
    """자연스러운 메시지 생성"""
    temp_diff = today_temp - yesterday_temp

    # 온도 변화 표현
    if temp_diff > 10:
        change = f"어제보다 {abs(temp_diff)}도 올라"
    elif temp_diff > 0:
        change = f"어제보다 {abs(temp_diff)}도 올라"
    elif temp_diff < -10:
        change = f"어제보다 {abs(temp_diff)}도 낮아져"
    elif temp_diff < 0:
        change = f"어제보다 {abs(temp_diff)}도 떨어져"
    else:
        # 온도 동일
        weather_words = ["비슷한", "같은"]
        return f"어제와 {random.choice(weather_words)} 날씨입니다. {get_activity_suggestion(today_temp, temp_diff)}"

    # 날씨 설명
    weather_desc = random.choice(get_weather_description(today_temp))

    # 활동 제안
    activity = get_activity_suggestion(today_temp, temp_diff)

    # 문장 조합
    message = f"{change} {weather_desc}. {activity}"

    return message


def generate_all_messages(original_data):
    """전체 데이터에 대해 새로운 메시지 생성"""
    new_data = []

    for yesterday, today, old_message in original_data:
        new_message = generate_natural_message(yesterday, today)
        new_data.append((yesterday, today, new_message))

    return new_data


def create_chat_format(yesterday, today, message):
    """Chat 형식으로 데이터 변환"""
    system_prompt = "당신은 공원 전광판 메시지 전문가입니다. 온도 정보를 받아 40-70자 길이의 간결한 한 문장 메시지를 작성하세요. 온도 차이를 구체적 숫자로 명시하고 공원 관련 조언을 포함하세요."

    text = f"""<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
어제 {yesterday}도, 오늘 {today}도<|im_end|>
<|im_start|>assistant
{message}<|im_end|>"""

    return text


def main():
    """메인 실행"""
    from wrap_temperature_data import TRAIN_DATA, VALIDATION_DATA

    print("=" * 70)
    print("자연스럽고 다양한 메시지 생성")
    print("=" * 70)
    print(f"\n학습 데이터: {len(TRAIN_DATA)}개")
    print(f"검증 데이터: {len(VALIDATION_DATA)}개\n")

    # 샘플 10개 먼저 확인
    print("샘플 10개 생성 결과:\n")
    for i in range(10):
        yesterday, today, old_message = TRAIN_DATA[i]
        new_message = generate_natural_message(yesterday, today)

        print(f"[{i+1}] 어제 {yesterday}도, 오늘 {today}도")
        print(f"  기존: {old_message}")
        print(f"  신규: {new_message}")
        print()

    print("\n전체 데이터 생성 중...\n")

    # 전체 데이터 생성
    new_train_data = generate_all_messages(TRAIN_DATA)
    new_val_data = generate_all_messages(VALIDATION_DATA)

    # JSONL 형식으로 저장
    train_file = "data/train_chat_diverse.jsonl"
    val_file = "data/validation_chat_diverse.jsonl"

    # 학습 데이터 저장
    with open(train_file, 'w', encoding='utf-8') as f:
        for yesterday, today, message in new_train_data:
            text = create_chat_format(yesterday, today, message)
            f.write(json.dumps({"text": text}, ensure_ascii=False) + '\n')

    # 검증 데이터 저장
    with open(val_file, 'w', encoding='utf-8') as f:
        for yesterday, today, message in new_val_data:
            text = create_chat_format(yesterday, today, message)
            f.write(json.dumps({"text": text}, ensure_ascii=False) + '\n')

    print("=" * 70)
    print("[OK] 생성 완료!")
    print("=" * 70)
    print(f"\n학습 데이터: {len(new_train_data)}개 → {train_file}")
    print(f"검증 데이터: {len(new_val_data)}개 → {val_file}")

    # 통계
    print("\n[다양성 통계]")
    locations_used = set()
    for _, _, msg in new_train_data[:50]:
        for loc in PARK_LOCATIONS:
            if loc in msg:
                locations_used.add(loc)

    print(f"사용된 공원 요소: {len(locations_used)}개")
    print(f"  {', '.join(list(locations_used)[:10])}")

    print("\n[다음 단계]")
    print("1. finetune_model_temperature.py 수정:")
    print(f"   TRAIN_FILE = '{train_file}'")
    print(f"   VAL_FILE = '{val_file}'")
    print("   OUTPUT_DIR = './finetuned_model_diverse'")
    print("\n2. 파인튜닝 실행:")
    print("   python scripts/finetune_model_temperature.py")
    print("\n3. .env 설정:")
    print("   ADAPTER_PATH=./finetuned_model_diverse")


if __name__ == "__main__":
    # 랜덤 시드 고정 (재현 가능하도록)
    random.seed(42)
    main()
