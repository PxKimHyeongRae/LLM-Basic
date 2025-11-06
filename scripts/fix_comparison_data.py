"""
생성된 온도 비교 데이터에서 '어제보다' 표현 일관성 보정
"""

import json
import re


def fix_temperature_data(input_file, output_file):
    """모든 출력 메시지에 '어제보다'가 포함되도록 수정"""
    fixed_data = []
    fix_count = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            output = item['output']

            # 숫자로 시작하는 메시지 찾기 (예: "10도 따뜻해졌습니다")
            if re.match(r'^\d+도', output):
                # "어제보다 " 추가
                output = "어제보다 " + output
                fix_count += 1

            # "기온이"로 시작하는 메시지도 수정
            if output.startswith("기온이"):
                output = "어제보다 " + output
                fix_count += 1

            item['output'] = output
            fixed_data.append(item)

    # 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in fixed_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✓ 총 {len(fixed_data)}개 중 {fix_count}개 수정 완료")
    print(f"✓ 저장: {output_file}")

    # 샘플 출력
    print("\n수정된 샘플 (5개):")
    import random
    for i, sample in enumerate(random.sample(fixed_data, 5), 1):
        print(f"\n[{i}] {sample['output']}")


if __name__ == "__main__":
    input_file = "data/training_data_comparison.jsonl"
    output_file = "data/training_data_comparison_fixed.jsonl"

    print("=" * 80)
    print("온도 비교 데이터 '어제보다' 표현 일관성 보정")
    print("=" * 80)

    fix_temperature_data(input_file, output_file)

    print("\n✓ 완료! 수정된 파일을 사용하세요.")
