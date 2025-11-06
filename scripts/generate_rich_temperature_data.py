"""
풍성한 온도 비교 데이터셋 생성
다양한 어휘와 표현을 조합하여 자연스러운 학습 데이터 생성
"""

import json
import random

# 공통 프롬프트 템플릿
INSTRUCTION = """<instruction>
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

<task>
입력: 어제 {yesterday}도, 오늘 {today}도
출력: {output}"""


# 온도 변화 표현 어휘
TEMP_INCREASE_VERBS = {
    "large": ["올라", "상승해", "올라가", "높아져", "오르면서"],  # 10도 이상
    "medium": ["올라", "높아져", "올라가", "상승해"],  # 5-9도
    "small": ["올라", "높아져", "올라가"],  # 1-4도
}

TEMP_DECREASE_VERBS = {
    "large": ["낮아져", "떨어져", "내려가", "하락해", "내려"],  # 10도 이상
    "medium": ["낮아져", "떨어져", "내려가", "내려"],  # 5-9도
    "small": ["낮아져", "내려가", "떨어져"],  # 1-4도
}

# 절대 온도에 따른 날씨 형용사
WEATHER_DESC = {
    "very_hot": ["무더워요", "더워졌습니다", "많이 덥습니다", "뜨거워요", "무척 덥습니다"],  # 30도 이상
    "hot": ["더워졌습니다", "따뜻해졌습니다", "덥습니다", "화창합니다"],  # 25-29도
    "warm": ["따뜻해졌습니다", "포근해졌습니다", "따뜻합니다", "온화합니다", "봄 날씨입니다"],  # 20-24도
    "mild": ["선선해졌습니다", "쾌적합니다", "좋은 날씨입니다", "시원해졌습니다"],  # 15-19도
    "cool": ["선선합니다", "시원해졌습니다", "쌀쌀해졌습니다", "서늘합니다"],  # 10-14도
    "cold": ["춥습니다", "쌀쌀합니다", "추워졌습니다", "차갑습니다"],  # 5-9도
    "very_cold": ["많이 춥습니다", "춥습니다", "매우 추워요", "영하의 날씨입니다"],  # 5도 미만
}

# 공원 활동 제안
PARK_ACTIVITIES = {
    "very_hot": [
        "공원 그늘에서 휴식하세요",
        "공원 분수대 근처가 시원합니다",
        "오전 산책을 권장합니다",
        "나무 그늘 아래가 좋아요",
        "시원한 그늘을 찾으세요",
        "공원 음수대를 이용하세요",
    ],
    "hot": [
        "공원 산책하기 좋아요",
        "야외 활동 즐기기 좋아요",
        "공원에서 여유를 즐기세요",
        "공원 나들이 즐기세요",
        "공원 벤치에서 휴식하세요",
        "가벼운 옷차림이 좋아요",
    ],
    "warm": [
        "공원 산책 완벽한 날이에요",
        "공원 산책하기 좋아요",
        "공원 나들이 최고예요",
        "공원에서 활동하기 좋아요",
        "공원 조깅하기 좋아요",
        "공원 벤치에서 책 읽기 좋아요",
    ],
    "mild": [
        "공원 산책 딱 좋은 날씨예요",
        "공원 산책 최고예요",
        "공원에서 여유를 즐기세요",
        "공원 산책로를 걸어보세요",
        "공원에서 편하게 쉬어가세요",
        "공원 벤치에 잠깐 앉아보세요",
    ],
    "cool": [
        "공원 산책 시 긴팔 챙기세요",
        "공원 방문 시 겉옷 챙기세요",
        "외출 시 가디건 챙기세요",
        "공원 산책로를 걸어보세요",
        "공원에서 가볍게 산책하세요",
    ],
    "cold": [
        "공원 방문 시 따뜻하게 입으세요",
        "외출 시 따뜻하게 입으세요",
        "공원 방문 시 겉옷 챙기세요",
        "두꺼운 옷 준비하세요",
        "공원 산책 시 목도리 챙기세요",
    ],
    "very_cold": [
        "공원 방문 시 두껍게 입으세요",
        "외출 시 따뜻하게 준비하세요",
        "방한 준비 철저히 하세요",
        "공원 방문 시 장갑 챙기세요",
        "실내 활동을 권장합니다",
    ],
}

# 동일 온도 표현
SAME_TEMP_PHRASES = [
    "어제와 비슷합니다",
    "어제와 같은 날씨입니다",
    "어제와 비슷한 날씨입니다",
    "기온이 비슷합니다",
]

# 동일 온도에서의 활동 제안
SAME_TEMP_ACTIVITIES = [
    "공원에서 여유를 즐기세요",
    "공원에서 편하게 쉬어가세요",
    "공원 산책 즐기세요",
    "공원 나들이 좋아요",
    "공원 벤치에 앉아 쉬어가세요",
]


def get_weather_category(temp):
    """절대 온도로 날씨 카테고리 결정"""
    if temp >= 30:
        return "very_hot"
    elif temp >= 25:
        return "hot"
    elif temp >= 20:
        return "warm"
    elif temp >= 15:
        return "mild"
    elif temp >= 10:
        return "cool"
    elif temp >= 5:
        return "cold"
    else:
        return "very_cold"


def get_change_magnitude(diff):
    """온도 변화 크기 카테고리"""
    abs_diff = abs(diff)
    if abs_diff >= 10:
        return "large"
    elif abs_diff >= 5:
        return "medium"
    else:
        return "small"


def generate_message(yesterday_temp, today_temp):
    """온도 입력으로 자연스러운 메시지 생성"""
    diff = today_temp - yesterday_temp

    # 온도 동일
    if diff == 0:
        phrase = random.choice(SAME_TEMP_PHRASES)
        activity = random.choice(SAME_TEMP_ACTIVITIES)
        return f"{phrase}. {activity}"

    # 온도 상승
    elif diff > 0:
        magnitude = get_change_magnitude(diff)
        verb = random.choice(TEMP_INCREASE_VERBS[magnitude])
        weather_cat = get_weather_category(today_temp)
        weather_desc = random.choice(WEATHER_DESC[weather_cat])
        activity = random.choice(PARK_ACTIVITIES[weather_cat])

        return f"어제보다 {abs(diff)}도 {verb} {weather_desc}. {activity}"

    # 온도 하강
    else:
        magnitude = get_change_magnitude(diff)
        verb = random.choice(TEMP_DECREASE_VERBS[magnitude])
        weather_cat = get_weather_category(today_temp)
        weather_desc = random.choice(WEATHER_DESC[weather_cat])
        activity = random.choice(PARK_ACTIVITIES[weather_cat])

        return f"어제보다 {abs(diff)}도 {verb} {weather_desc}. {activity}"


def generate_dataset():
    """풍성한 데이터셋 생성"""
    dataset = []

    # 1. 큰 온도 상승 (10-20도 상승)
    for yesterday in range(-10, 26, 3):
        for increase in [10, 12, 13, 15, 18, 20]:
            today = yesterday + increase
            if -15 <= today <= 38:
                message = generate_message(yesterday, today)
                text = INSTRUCTION.format(yesterday=yesterday, today=today, output=message)
                dataset.append({"text": text})

    # 2. 중간 온도 상승 (5-9도 상승)
    for yesterday in range(-10, 28, 2):
        for increase in [5, 6, 7, 8, 9]:
            today = yesterday + increase
            if -15 <= today <= 38:
                message = generate_message(yesterday, today)
                text = INSTRUCTION.format(yesterday=yesterday, today=today, output=message)
                dataset.append({"text": text})

    # 3. 작은 온도 상승 (1-4도 상승)
    for yesterday in range(-10, 32, 3):
        for increase in [1, 2, 3, 4]:
            today = yesterday + increase
            if -15 <= today <= 38:
                message = generate_message(yesterday, today)
                text = INSTRUCTION.format(yesterday=yesterday, today=today, output=message)
                dataset.append({"text": text})

    # 4. 큰 온도 하강 (10-20도 하강)
    for yesterday in range(10, 36, 3):
        for decrease in [10, 12, 13, 15, 18, 20]:
            today = yesterday - decrease
            if -15 <= today <= 38:
                message = generate_message(yesterday, today)
                text = INSTRUCTION.format(yesterday=yesterday, today=today, output=message)
                dataset.append({"text": text})

    # 5. 중간 온도 하강 (5-9도 하강)
    for yesterday in range(5, 36, 2):
        for decrease in [5, 6, 7, 8, 9]:
            today = yesterday - decrease
            if -15 <= today <= 38:
                message = generate_message(yesterday, today)
                text = INSTRUCTION.format(yesterday=yesterday, today=today, output=message)
                dataset.append({"text": text})

    # 6. 작은 온도 하강 (1-4도 하강)
    for yesterday in range(0, 36, 3):
        for decrease in [1, 2, 3, 4]:
            today = yesterday - decrease
            if -15 <= today <= 38:
                message = generate_message(yesterday, today)
                text = INSTRUCTION.format(yesterday=yesterday, today=today, output=message)
                dataset.append({"text": text})

    # 7. 온도 동일
    for temp in range(-10, 36, 2):
        message = generate_message(temp, temp)
        text = INSTRUCTION.format(yesterday=temp, today=temp, output=message)
        dataset.append({"text": text})

    # 8. 극단적 케이스 추가
    extreme_cases = [
        (-15, 10, "어제보다 25도 올라 훨씬 포근해졌습니다. 공원 나들이 즐기세요."),
        (35, 15, "어제보다 20도 낮아져 시원해졌습니다. 공원 산책하기 좋아요."),
        (38, 28, "어제보다 10도 낮아져 선선해졌습니다. 공원 산책 좋아요."),
        (-10, -2, "어제보다 8도 올라 조금 포근해졌습니다. 방한은 필수입니다."),
        (0, 20, "어제보다 20도 올라 따뜻해졌습니다. 공원 산책 완벽한 날이에요."),
    ]

    for yesterday, today, message in extreme_cases:
        text = INSTRUCTION.format(yesterday=yesterday, today=today, output=message)
        dataset.append({"text": text})

    # 중복 제거 (동일한 온도 조합)
    seen = set()
    unique_dataset = []
    for item in dataset:
        # 입력 온도 조합을 키로 사용
        key = (item["text"].split("입력: ")[1].split("\n")[0])
        if key not in seen:
            seen.add(key)
            unique_dataset.append(item)

    # 셔플
    random.shuffle(unique_dataset)

    return unique_dataset


def main():
    print("=" * 70)
    print("풍성한 온도 비교 데이터셋 생성")
    print("=" * 70)

    # 데이터 생성
    dataset = generate_dataset()

    print(f"\n총 생성된 데이터: {len(dataset)}개")

    # 학습/검증 분리 (90% / 10%)
    split_idx = int(len(dataset) * 0.9)
    train_data = dataset[:split_idx]
    val_data = dataset[split_idx:]

    # 저장
    train_file = "data/train_temperature.jsonl"
    val_file = "data/validation_temperature.jsonl"

    with open(train_file, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    with open(val_file, 'w', encoding='utf-8') as f:
        for item in val_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"\n✅ 학습 데이터: {len(train_data)}개 → {train_file}")
    print(f"✅ 검증 데이터: {len(val_data)}개 → {val_file}")

    # 샘플 출력
    print("\n" + "=" * 70)
    print("샘플 데이터 (3개):")
    print("=" * 70)
    for i in range(min(3, len(train_data))):
        sample = train_data[i]["text"]
        lines = sample.split('\n')
        for line in lines:
            if line.startswith("입력:") or line.startswith("출력:"):
                print(line)
        print("-" * 70)

    print("\n✅ 데이터 생성 완료!")


if __name__ == "__main__":
    main()
