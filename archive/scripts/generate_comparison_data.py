"""
온도 비교 학습 데이터 대량 생성 스크립트

목표: 200개 이상의 온도 비교 시나리오 데이터 생성
- 다양한 온도 차이 (-30도 ~ +30도)
- 다양한 기준 온도 (-10도, 0도, 10도, 20도, 30도)
- 자연스러운 한국어 표현
"""

import json
import random
from pathlib import Path


def generate_temperature_comparison_data():
    """온도 비교 학습 데이터 생성"""
    dataset = []

    # 온도 차이별 표현 템플릿
    def get_temperature_message(yesterday: int, today: int) -> str:
        """온도 변화에 따른 적절한 메시지 생성"""
        diff = today - yesterday
        abs_diff = abs(diff)

        # 온도 차이가 거의 없음 (0-1도)
        if abs_diff <= 1:
            if diff > 0:
                messages = [
                    f"어제보다 {abs_diff}도 따뜻해졌습니다. 산책하기 좋은 날씨예요.",
                    f"어제와 비슷하지만 {abs_diff}도 올랐습니다. 쾌적한 하루 되세요.",
                ]
            elif diff < 0:
                messages = [
                    f"어제보다 {abs_diff}도 시원해졌습니다. 상쾌한 날씨예요.",
                    f"어제와 비슷하지만 {abs_diff}도 내렸습니다. 편안한 하루 되세요.",
                ]
            else:
                messages = [
                    "어제와 기온이 같습니다. 안정적인 날씨가 계속됩니다.",
                ]

        # 작은 변화 (2-4도)
        elif 2 <= abs_diff <= 4:
            if diff > 0:
                messages = [
                    f"어제보다 {abs_diff}도 따뜻해졌습니다. 가벼운 옷차림이 좋겠어요.",
                    f"{abs_diff}도 상승해 포근합니다. 산책하기 좋은 날씨예요.",
                    f"어제보다 {abs_diff}도 올라 따뜻합니다. 공원 나들이 추천드려요.",
                ]
            else:
                messages = [
                    f"어제보다 {abs_diff}도 시원해졌습니다. 상쾌한 날씨예요.",
                    f"{abs_diff}도 하강해 선선합니다. 외출하기 좋은 날씨예요.",
                    f"어제보다 {abs_diff}도 내려 시원합니다. 가벼운 산책 어떠세요?",
                ]

        # 중간 변화 (5-9도)
        elif 5 <= abs_diff <= 9:
            if diff > 0:
                messages = [
                    f"어제보다 {abs_diff}도 상승해 따뜻합니다. 얇은 옷을 권장합니다.",
                    f"{abs_diff}도 따뜻해졌습니다. 가벼운 옷차림으로 외출하세요.",
                    f"어제보다 {abs_diff}도 올라 포근합니다. 즐거운 하루 되세요.",
                ]
            else:
                messages = [
                    f"어제보다 {abs_diff}도 하강했습니다. 외출 시 겉옷을 챙기세요.",
                    f"{abs_diff}도 추워졌습니다. 가디건이나 재킷을 준비하세요.",
                    f"어제보다 {abs_diff}도 내려 선선합니다. 얇은 겉옷이 필요해요.",
                ]

        # 큰 변화 (10-14도)
        elif 10 <= abs_diff <= 14:
            if diff > 0:
                messages = [
                    f"어제보다 {abs_diff}도 상승해 매우 덥습니다. 물을 충분히 마시세요.",
                    f"{abs_diff}도 따뜻해져 더워졌습니다. 수분 섭취에 신경 쓰세요.",
                    f"어제보다 {abs_diff}도 올라 많이 덥습니다. 햇볕 조심하세요.",
                ]
            else:
                messages = [
                    f"어제보다 {abs_diff}도 하강해 쌀쌀합니다. 따뜻하게 입으세요.",
                    f"{abs_diff}도 추워졌습니다. 외출 시 두꺼운 옷을 착용하세요.",
                    f"어제보다 {abs_diff}도 내려 매우 춥습니다. 체온 유지 주의하세요.",
                ]

        # 매우 큰 변화 (15-19도)
        elif 15 <= abs_diff <= 19:
            if diff > 0:
                messages = [
                    f"어제보다 {abs_diff}도 급상승했습니다. 폭염 주의하세요.",
                    f"{abs_diff}도 상승해 매우 덥습니다. 그늘에서 휴식하세요.",
                    f"기온이 {abs_diff}도나 올랐습니다. 열사병 조심하세요.",
                ]
            else:
                messages = [
                    f"어제보다 {abs_diff}도 급강하했습니다. 감기 조심하세요.",
                    f"{abs_diff}도 하강해 매우 춥습니다. 방한에 주의하세요.",
                    f"기온이 {abs_diff}도나 떨어졌습니다. 따뜻하게 입고 외출하세요.",
                ]

        # 극단적 변화 (20도 이상)
        else:  # abs_diff >= 20
            if diff > 0:
                messages = [
                    f"어제보다 {abs_diff}도 상승해 위험합니다. 야외활동 자제하세요.",
                    f"{abs_diff}도 급상승! 폭염경보 수준입니다. 실내에 머무세요.",
                    f"기온이 {abs_diff}도 치솟았습니다. 무리한 활동 삼가세요.",
                ]
            else:
                messages = [
                    f"어제보다 {abs_diff}도 하강해 매우 춥습니다. 외출 자제하세요.",
                    f"{abs_diff}도 급강하! 한파경보 수준입니다. 보온에 주의하세요.",
                    f"기온이 {abs_diff}도 폭락했습니다. 체온 유지에 각별히 주의하세요.",
                ]

        return random.choice(messages)

    # 1. 다양한 온도 차이 생성 (중복 없이)
    scenarios = []

    # 주요 온도 구간별로 데이터 생성
    base_temperatures = [-15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35]

    # 각 기준 온도에서 다양한 변화량 적용
    for base_temp in base_temperatures:
        # 작은 변화 (±1~4도)
        for diff in range(-4, 5):
            if diff == 0:
                continue
            yesterday = base_temp
            today = base_temp + diff
            scenarios.append((yesterday, today))

        # 중간 변화 (±5~10도) - 일부만
        for diff in [5, 6, 7, 8, 9, 10, -5, -6, -7, -8, -9, -10]:
            yesterday = base_temp
            today = base_temp + diff
            scenarios.append((yesterday, today))

        # 큰 변화 (±11~20도) - 선별적으로
        for diff in [11, 13, 15, 17, 20, -11, -13, -15, -17, -20]:
            yesterday = base_temp
            today = base_temp + diff
            # 현실적인 온도 범위만 (-20~45도)
            if -20 <= today <= 45:
                scenarios.append((yesterday, today))

    # 극단적 변화 (±20도 이상) - 특별 케이스
    extreme_cases = [
        (-10, 10),   # +20도
        (0, 20),     # +20도
        (10, -10),   # -20도
        (20, 0),     # -20도
        (5, 30),     # +25도
        (30, 5),     # -25도
        (0, 30),     # +30도
        (30, 0),     # -30도
    ]
    scenarios.extend(extreme_cases)

    # 중복 제거 및 정렬
    scenarios = list(set(scenarios))
    scenarios.sort()

    print(f"총 {len(scenarios)}개의 온도 비교 시나리오 생성 중...")

    # 데이터셋 생성
    for yesterday, today in scenarios:
        message = get_temperature_message(yesterday, today)

        dataset.append({
            "input": f"어제의 평균온도는 {yesterday}도고 오늘의 평균온도는 {today}도야. "
                     f"이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘",
            "output": message
        })

    return dataset


def save_to_jsonl(dataset: list, output_path: str):
    """JSONL 형식으로 저장"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✓ 데이터 저장 완료: {output_path}")


def print_statistics(dataset: list):
    """데이터셋 통계 출력"""
    print("\n" + "=" * 80)
    print("데이터셋 통계")
    print("=" * 80)

    # 온도 차이 분포 분석
    from collections import Counter

    temp_diffs = []
    for item in dataset:
        input_text = item['input']
        # "어제의 평균온도는 {yesterday}도고 오늘의 평균온도는 {today}도야"에서 추출
        import re
        match = re.search(r'어제의 평균온도는 (-?\d+)도고 오늘의 평균온도는 (-?\d+)도야', input_text)
        if match:
            yesterday = int(match.group(1))
            today = int(match.group(2))
            diff = today - yesterday
            temp_diffs.append(diff)

    diff_counter = Counter(temp_diffs)

    print(f"\n총 데이터 개수: {len(dataset)}")
    print(f"\n온도 차이 범위: {min(temp_diffs)}도 ~ {max(temp_diffs)}도")

    # 구간별 분포
    print("\n온도 차이 구간별 분포:")
    ranges = [
        ("0-1도", 0, 1),
        ("2-4도", 2, 4),
        ("5-9도", 5, 9),
        ("10-14도", 10, 14),
        ("15-19도", 15, 19),
        ("20도 이상", 20, 100),
    ]

    for label, min_val, max_val in ranges:
        count_pos = sum(1 for d in temp_diffs if min_val <= d <= max_val)
        count_neg = sum(1 for d in temp_diffs if -max_val <= d <= -min_val)
        print(f"  {label:12s}: 상승 {count_pos:3d}개, 하강 {count_neg:3d}개")

    # 샘플 출력
    print("\n샘플 데이터 (5개):")
    print("-" * 80)
    for i, sample in enumerate(random.sample(dataset, min(5, len(dataset))), 1):
        print(f"\n[샘플 {i}]")
        print(f"입력: {sample['input'][:60]}...")
        print(f"출력: {sample['output']}")

    print("\n" + "=" * 80)


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("온도 비교 학습 데이터 생성 시작")
    print("=" * 80)

    # 데이터 생성
    dataset = generate_temperature_comparison_data()

    # 통계 출력
    print_statistics(dataset)

    # JSONL 저장
    output_path = "data/training_data_comparison.jsonl"
    save_to_jsonl(dataset, output_path)

    print(f"\n✓ 완료! {len(dataset)}개의 온도 비교 데이터가 생성되었습니다.")
    print(f"✓ 저장 위치: {output_path}")

    # 기존 데이터와 병합 안내
    print("\n다음 단계:")
    print("1. 기존 training_data.jsonl과 병합")
    print("2. 재파인튜닝 실행")
    print("3. A/B 테스트로 성능 비교")


if __name__ == "__main__":
    main()
