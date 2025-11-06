"""
파인튜닝용 데이터 준비 스크립트
기존 데이터를 새로운 구조화된 프롬프트 형식으로 변환합니다.
"""

import json
import os
from pathlib import Path


def create_structured_prompt(input_text: str, output_text: str) -> dict:
    """
    구조화된 프롬프트 형식으로 학습 데이터를 생성합니다.

    학습 데이터는 "프롬프트 + 정답" 형식으로 구성됩니다.
    모델이 이 형식에 익숙해지도록 학습시킵니다.
    """

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

    # 정답은 깔끔한 한 문장만
    answer = output_text.strip()

    # 학습 데이터: 전체 대화 (프롬프트 + 정답)
    full_text = f"{prompt} {answer}"

    return {
        "prompt": prompt,
        "completion": answer,
        "text": full_text  # SFTTrainer가 사용할 전체 텍스트
    }


def prepare_temperature_comparison_data():
    """
    온도 비교 데이터를 생성합니다.
    다양한 온도 변화 시나리오를 커버합니다.
    """

    training_data = []

    # 1. 큰 온도 하강 (10도 이상)
    scenarios = [
        # (어제, 오늘, 메시지)
        (25, 10, "어제보다 15도 급격히 낮아졌습니다. 따뜻한 옷을 꼭 챙기세요."),
        (30, 15, "어제보다 15도 하강해 쌀쌀합니다. 외출 시 겉옷 필수예요."),
        (20, 5, "어제보다 15도 낮아져 매우 춥습니다. 방한 준비 철저히 하세요."),
        (15, -5, "어제보다 20도 급락했습니다. 동파 주의하시고 보온 잘하세요."),
        (10, -10, "어제보다 20도 하강해 혹독한 추위입니다. 외출 주의하세요."),

        # 2. 큰 온도 상승 (10도 이상)
        (10, 25, "어제보다 15도 올라 따뜻해졌습니다. 가벼운 옷차림이 좋겠어요."),
        (5, 20, "어제보다 15도 상승해 포근합니다. 산책하기 좋은 날씨예요."),
        (15, 30, "어제보다 15도 올라 더워졌습니다. 수분 섭취 충분히 하세요."),
        (20, 35, "어제보다 15도 급상승해 무더워요. 물을 자주 마시세요."),
        (-5, 10, "어제보다 15도 올라 훨씬 포근합니다. 좋은 하루 되세요."),

        # 3. 중간 온도 하강 (5-10도)
        (20, 15, "어제보다 5도 낮아졌습니다. 가벼운 겉옷 챙기세요."),
        (25, 18, "어제보다 7도 하강했습니다. 아침저녁으로 쌀쌀해요."),
        (18, 10, "어제보다 8도 낮아져 쌀쌀합니다. 따뜻하게 입으세요."),
        (15, 8, "어제보다 7도 하강해 춥습니다. 외출 시 겉옷 챙기세요."),
        (12, 5, "어제보다 7도 낮아졌습니다. 방한 준비 하시길 바랍니다."),

        # 4. 중간 온도 상승 (5-10도)
        (10, 18, "어제보다 8도 올라 포근해졌습니다. 산책하기 좋은 날씨예요."),
        (15, 22, "어제보다 7도 상승해 따뜻합니다. 좋은 하루 보내세요."),
        (8, 15, "어제보다 7도 올라 훨씬 포근합니다. 즐거운 하루 되세요."),
        (5, 13, "어제보다 8도 상승했습니다. 외출하기 좋은 날씨예요."),
        (18, 25, "어제보다 7도 올라 따뜻해졌습니다. 가벼운 옷차림 추천해요."),

        # 5. 작은 온도 변화 (1-4도)
        (15, 18, "어제보다 3도 올라 조금 포근해졌습니다. 좋은 하루 되세요."),
        (20, 22, "어제보다 2도 상승했습니다. 산책하기 좋은 날씨예요."),
        (18, 15, "어제보다 3도 낮아졌습니다. 가벼운 겉옷 챙기세요."),
        (22, 19, "어제보다 3도 하강했습니다. 쾌적한 날씨가 이어져요."),
        (16, 17, "어제와 비슷한 날씨입니다. 산책하기 좋은 하루예요."),

        # 6. 극한 온도 (매우 덥거나 추움)
        (32, 38, "어제보다 6도 상승해 폭염 수준입니다. 외출 자제하세요."),
        (35, 40, "어제보다 5도 올라 매우 더워요. 실내 활동 권장합니다."),
        (-15, -10, "어제보다 5도 올랐지만 여전히 혹한입니다. 외출 주의하세요."),
        (-10, -18, "어제보다 8도 하강해 극심한 추위입니다. 동파 주의하세요."),
        (38, 42, "어제보다 4도 상승해 위험한 더위입니다. 냉방 시설 이용하세요."),

        # 7. 계절 전환기
        (8, 15, "어제보다 7도 올라 봄 날씨입니다. 산책하기 좋아요."),
        (28, 22, "어제보다 6도 낮아져 선선합니다. 가을 날씨가 시작돼요."),
        (12, 5, "어제보다 7도 하강해 겨울이 다가옵니다. 따뜻하게 입으세요."),
        (15, 24, "어제보다 9도 올라 여름 같은 날씨입니다. 가볍게 입으세요."),
    ]

    for yesterday, today, message in scenarios:
        input_text = f"어제 {yesterday}도, 오늘 {today}도"
        training_data.append(create_structured_prompt(input_text, message))

    return training_data


def prepare_general_weather_data():
    """
    일반적인 날씨 상황에 대한 메시지 데이터를 생성합니다.
    """

    training_data = []

    scenarios = [
        # (입력, 출력)
        ("폭염주의보 발령, 온도 37도", "폭염주의보가 발령되었습니다. 야외활동 자제하고 수분 섭취하세요."),
        ("미세먼지 매우나쁨, 외출자제", "미세먼지 농도가 매우 나쁩니다. 외출 시 마스크 착용하세요."),
        ("한파경보, 기온 -12도", "한파경보가 발령되었습니다. 외출 주의하고 동파 대비하세요."),
        ("일교차 15도, 아침 5도 낮 20도", "일교차가 15도로 큽니다. 겉옷을 꼭 챙기세요."),
        ("습도 88%, 찜통더위", "습도가 높아 체감온도가 높습니다. 시원한 곳에서 휴식하세요."),
        ("쾌적한 날씨, 온도 24도 습도 55%", "산책하기 좋은 완벽한 날씨입니다. 좋은 하루 되세요."),
        ("비 예보, 우산 필수", "오늘 비 소식이 있습니다. 우산 꼭 챙기세요."),
        ("눈 예보, 미끄러움 주의", "오늘 눈이 내립니다. 미끄러운 길 조심하세요."),
        ("강풍주의보, 바람 강함", "바람이 강하게 붑니다. 외출 시 주의하세요."),
        ("황사경보, 마스크 착용", "황사가 발생했습니다. 외출 시 마스크 착용하세요."),
    ]

    for input_text, output_text in scenarios:
        training_data.append(create_structured_prompt(input_text, output_text))

    return training_data


def main():
    """메인 실행 함수"""

    print("=" * 70)
    print("파인튜닝 데이터 준비 시작")
    print("=" * 70)

    # 데이터 디렉토리 생성
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # 1. 온도 비교 데이터 생성
    print("\n1. 온도 비교 데이터 생성 중...")
    temp_comparison_data = prepare_temperature_comparison_data()
    print(f"   생성된 데이터: {len(temp_comparison_data)}개")

    # 2. 일반 날씨 데이터 생성
    print("\n2. 일반 날씨 데이터 생성 중...")
    general_weather_data = prepare_general_weather_data()
    print(f"   생성된 데이터: {len(general_weather_data)}개")

    # 3. 전체 데이터 합치기
    all_data = temp_comparison_data + general_weather_data
    total_count = len(all_data)
    print(f"\n3. 전체 데이터: {total_count}개")

    # 4. Train/Validation 분할 (90:10)
    split_idx = int(total_count * 0.9)
    train_data = all_data[:split_idx]
    val_data = all_data[split_idx:]

    print(f"   - 학습 데이터: {len(train_data)}개")
    print(f"   - 검증 데이터: {len(val_data)}개")

    # 5. JSONL 파일로 저장
    train_file = data_dir / "train_structured.jsonl"
    val_file = data_dir / "validation_structured.jsonl"

    print(f"\n4. 파일 저장 중...")

    with open(train_file, 'w', encoding='utf-8') as f:
        for item in train_data:
            # SFTTrainer는 'text' 필드를 사용
            f.write(json.dumps({"text": item["text"]}, ensure_ascii=False) + '\n')

    with open(val_file, 'w', encoding='utf-8') as f:
        for item in val_data:
            f.write(json.dumps({"text": item["text"]}, ensure_ascii=False) + '\n')

    print(f"   ✓ 학습 데이터: {train_file}")
    print(f"   ✓ 검증 데이터: {val_file}")

    # 6. 샘플 출력
    print("\n" + "=" * 70)
    print("생성된 데이터 샘플:")
    print("=" * 70)
    print("\n[샘플 1 - 온도 비교]")
    print(train_data[0]["text"])
    print("\n[샘플 2 - 일반 날씨]")
    print(train_data[-1]["text"])

    print("\n" + "=" * 70)
    print("✅ 데이터 준비 완료!")
    print("=" * 70)
    print("\n다음 단계: 파인튜닝 실행")
    print("  python scripts/finetune_model_v2.py")


if __name__ == "__main__":
    main()
