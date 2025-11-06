"""
대량의 학습 데이터 생성 스크립트
파인튜닝 성능 향상을 위해 다양한 패턴 생성
"""

import json
import random
from pathlib import Path


def generate_temperature_variations():
    """다양한 온도 변화 패턴 생성 (200개)"""

    data = []

    # 온도 범위: -20도 ~ 45도
    temp_range = list(range(-20, 46))

    # 변화량별 표현 템플릿
    templates = {
        'large_increase': [  # 10도 이상 상승
            "어제보다 {diff}도 올라 따뜻해졌습니다. 가벼운 옷차림 추천해요.",
            "어제보다 {diff}도 상승해 포근합니다. 산책하기 좋은 날씨예요.",
            "어제보다 {diff}도 급상승했습니다. 외출하기 좋은 날씨입니다.",
        ],
        'large_decrease': [  # 10도 이상 하강
            "어제보다 {diff}도 낮아졌습니다. 따뜻한 옷을 꼭 챙기세요.",
            "어제보다 {diff}도 하강해 쌀쌀합니다. 외출 시 겉옷 필수예요.",
            "어제보다 {diff}도 급락했습니다. 방한 준비 철저히 하세요.",
        ],
        'medium_increase': [  # 5-10도 상승
            "어제보다 {diff}도 올라 포근해졌습니다. 좋은 하루 보내세요.",
            "어제보다 {diff}도 상승했습니다. 외출하기 좋은 날씨예요.",
            "어제보다 {diff}도 올라 훨씬 따뜻합니다. 즐거운 하루 되세요.",
        ],
        'medium_decrease': [  # 5-10도 하강
            "어제보다 {diff}도 낮아졌습니다. 가벼운 겉옷 챙기세요.",
            "어제보다 {diff}도 하강했습니다. 아침저녁으로 쌀쌀해요.",
            "어제보다 {diff}도 내려갔습니다. 외출 시 겉옷 챙기세요.",
        ],
        'small_increase': [  # 1-4도 상승
            "어제보다 {diff}도 올라 조금 포근해졌습니다. 좋은 하루 되세요.",
            "어제보다 {diff}도 상승했습니다. 산책하기 좋은 날씨예요.",
            "어제와 비슷하지만 {diff}도 더 따뜻합니다. 쾌적한 하루예요.",
        ],
        'small_decrease': [  # 1-4도 하강
            "어제보다 {diff}도 낮아졌습니다. 가벼운 겉옷 챙기세요.",
            "어제보다 {diff}도 하강했습니다. 쾌적한 날씨가 이어져요.",
            "어제와 비슷하지만 {diff}도 더 시원합니다. 좋은 하루 되세요.",
        ],
        'no_change': [
            "어제와 비슷한 날씨입니다. 산책하기 좋은 하루예요.",
            "어제와 동일한 기온입니다. 즐거운 하루 보내세요.",
            "날씨 변화가 없습니다. 편안한 하루 되세요.",
        ]
    }

    # 200개 생성
    for _ in range(200):
        yesterday = random.choice(temp_range)

        # 변화량 결정 (다양한 패턴)
        change_type = random.choice([
            'large_increase', 'large_decrease',
            'medium_increase', 'medium_decrease',
            'small_increase', 'small_decrease',
            'no_change'
        ])

        if change_type == 'large_increase':
            diff = random.randint(10, 20)
            today = yesterday + diff
        elif change_type == 'large_decrease':
            diff = random.randint(10, 20)
            today = yesterday - diff
        elif change_type == 'medium_increase':
            diff = random.randint(5, 9)
            today = yesterday + diff
        elif change_type == 'medium_decrease':
            diff = random.randint(5, 9)
            today = yesterday - diff
        elif change_type == 'small_increase':
            diff = random.randint(1, 4)
            today = yesterday + diff
        elif change_type == 'small_decrease':
            diff = random.randint(1, 4)
            today = yesterday - diff
        else:  # no_change
            diff = 0
            today = yesterday

        # 범위 체크
        if today < -20 or today > 45:
            continue

        # 메시지 선택
        message_template = random.choice(templates[change_type])
        message = message_template.format(diff=abs(diff))

        input_text = f"어제 {yesterday}도, 오늘 {today}도"

        data.append({
            'input': input_text,
            'output': message
        })

    return data


def generate_extreme_weather():
    """극한 날씨 상황 (50개)"""

    scenarios = []

    # 폭염
    for temp in range(35, 45):
        scenarios.append({
            'input': f"폭염주의보, 현재 온도 {temp}도",
            'output': f"폭염주의보 발령, 기온 {temp}도입니다. 야외활동 자제하고 수분 섭취하세요."
        })

    # 한파
    for temp in range(-20, -5):
        scenarios.append({
            'input': f"한파경보, 현재 온도 {temp}도",
            'output': f"한파경보 발령, 기온 {temp}도입니다. 외출 주의하고 동파 대비하세요."
        })

    # 일교차
    for diff in range(10, 21):
        scenarios.append({
            'input': f"일교차 {diff}도, 아침 5도 낮 {5+diff}도",
            'output': f"일교차가 {diff}도로 큽니다. 외출 시 겉옷을 꼭 챙기세요."
        })

    # 습도
    for humidity in range(80, 96, 5):
        scenarios.append({
            'input': f"습도 {humidity}%, 찜통더위",
            'output': f"습도가 {humidity}%로 높아 체감온도가 높습니다. 시원한 곳에서 휴식하세요."
        })

    return scenarios


def generate_weather_conditions():
    """다양한 날씨 조건 (50개)"""

    conditions = [
        ("비 예보, 강수확률 80%", "오늘 비 소식이 있습니다. 우산 꼭 챙기세요."),
        ("눈 예보, 적설량 5cm", "오늘 눈이 내립니다. 미끄러운 길 조심하세요."),
        ("강풍주의보, 초속 15m", "바람이 강하게 붑니다. 외출 시 주의하세요."),
        ("황사경보 발령", "황사가 발생했습니다. 외출 시 마스크 착용하세요."),
        ("미세먼지 매우나쁨", "미세먼지 농도가 매우 나쁩니다. 외출 시 마스크 착용하세요."),
        ("미세먼지 나쁨", "미세먼지 농도가 나쁩니다. 외출 자제 권장합니다."),
        ("안개주의보", "짙은 안개로 시야가 불량합니다. 운전 주의하세요."),
        ("태풍주의보", "태풍 영향권입니다. 외출 자제하시기 바랍니다."),
        ("호우주의보", "많은 비가 예상됩니다. 저지대 침수 주의하세요."),
        ("폭설주의보", "많은 눈이 예상됩니다. 교통 혼잡 예상되니 주의하세요."),
    ]

    # 각 조건을 5번씩 반복하되 약간씩 변형
    scenarios = []
    for input_text, output_text in conditions:
        for i in range(5):
            scenarios.append({
                'input': input_text,
                'output': output_text
            })

    return scenarios


def create_structured_prompt(input_text: str, output_text: str) -> dict:
    """구조화된 프롬프트 생성"""

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

<task>
입력: {input_text}
출력:"""

    answer = output_text.strip()
    full_text = f"{prompt} {answer}"

    return {
        "text": full_text,
        "input": input_text,
        "output": output_text
    }


def main():
    print("=" * 70)
    print("대량 학습 데이터 생성 (목표: 300개)")
    print("=" * 70)

    # 데이터 생성
    print("\n1. 온도 변화 패턴 생성 중... (200개)")
    temp_data = generate_temperature_variations()
    print(f"   생성 완료: {len(temp_data)}개")

    print("\n2. 극한 날씨 상황 생성 중... (50개)")
    extreme_data = generate_extreme_weather()
    print(f"   생성 완료: {len(extreme_data)}개")

    print("\n3. 날씨 조건 생성 중... (50개)")
    weather_data = generate_weather_conditions()
    print(f"   생성 완료: {len(weather_data)}개")

    # 전체 데이터 합치기
    all_data = temp_data + extreme_data + weather_data

    # 중복 제거
    unique_data = []
    seen = set()
    for item in all_data:
        key = item['input']
        if key not in seen:
            seen.add(key)
            unique_data.append(item)

    print(f"\n4. 총 데이터: {len(unique_data)}개 (중복 제거 후)")

    # 셔플
    random.shuffle(unique_data)

    # Train/Validation 분할 (90:10)
    split_idx = int(len(unique_data) * 0.9)
    train_data = unique_data[:split_idx]
    val_data = unique_data[split_idx:]

    print(f"   - 학습 데이터: {len(train_data)}개")
    print(f"   - 검증 데이터: {len(val_data)}개")

    # 구조화된 프롬프트로 변환
    print("\n5. 구조화된 프롬프트로 변환 중...")
    train_structured = [create_structured_prompt(d['input'], d['output']) for d in train_data]
    val_structured = [create_structured_prompt(d['input'], d['output']) for d in val_data]

    # 저장
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    train_file = data_dir / "train_large.jsonl"
    val_file = data_dir / "validation_large.jsonl"

    print(f"\n6. 파일 저장 중...")

    with open(train_file, 'w', encoding='utf-8') as f:
        for item in train_structured:
            f.write(json.dumps({"text": item["text"]}, ensure_ascii=False) + '\n')

    with open(val_file, 'w', encoding='utf-8') as f:
        for item in val_structured:
            f.write(json.dumps({"text": item["text"]}, ensure_ascii=False) + '\n')

    print(f"   ✓ 학습 데이터: {train_file}")
    print(f"   ✓ 검증 데이터: {val_file}")

    # 샘플 출력
    print("\n" + "=" * 70)
    print("생성된 데이터 샘플:")
    print("=" * 70)

    for i in range(3):
        print(f"\n[샘플 {i+1}]")
        print(f"입력: {train_structured[i]['input']}")
        print(f"출력: {train_structured[i]['output']}")

    print("\n" + "=" * 70)
    print("✅ 대량 데이터 생성 완료!")
    print("=" * 70)
    print("\n다음 단계:")
    print("  python scripts/finetune_model_large.py")


if __name__ == "__main__":
    main()
