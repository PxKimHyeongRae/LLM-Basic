"""
DPO (Direct Preference Optimization) 데이터셋 생성

목표:
- 좋은 출력 vs 나쁜 출력 쌍 생성
- 규칙 없이 선호도 학습
- 자동으로 깔끔한 출력 생성
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv
import random

load_dotenv()


def load_current_model_outputs():
    """
    현재 파인튜닝된 모델의 출력을 불러옵니다.
    (나쁜 예시로 사용)

    테스트 케이스로부터 생성된 출력을 사용하거나,
    실제 모델 실행 결과를 사용할 수 있습니다.
    """
    # 테스트 케이스 (사용자가 제공한 실제 문제 사례)
    bad_examples = [
        {
            "prompt": "어제의 평균온도는 0도고 오늘의 평균온도는 1도야. 이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘",
            "rejected": ".\n전광판에 표시할 메시지:\n\n안녕하세요, 오늘 공원은 더 시원합니다. 외출 시 가벼운 겉옷을 챙기세요. 감사합니다. 2월 5일 (화요일) 오전 9시 38분\n</think>\n\n오늘 공원",
        },
        {
            "prompt": "어제의 평균온도는 -10도고 오늘의 평균온도는 10도야. 이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘",
            "rejected": ".\n전광판에 표시할 메시지: \"오늘은 따뜻해졌어요! 공원에 오셔서 산책을 즐기세요.\"\n\n이 메시지가 적절한가요? 아니면 더 나은 제안이 있나요?",
        },
        {
            "prompt": "어제의 평균온도는 10도고 오늘의 평균온도는 -10도야. 이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘",
            "rejected": ".\n전광판에 표시할 메시지:\n\n오늘 공원은 매우 추워요, 따뜻한 옷을 입고 오세요. 난방이 되지 않는 야외 공간이므로 외출 시 주의가 필요합니다.",
        },
        {
            "prompt": "어제의 평균온도는 20도고 오늘의 평균온도는 30도야. 이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘",
            "rejected": ".\n전광판에 표시할 메시지:\n\n안녕하세요, 오늘은 평균기온이 어제보다 10도나 상승해 매우 덥습니다. 물을 충분히 마시고, 햇빛에 장시간 노출되지 않도록 주의하시기 바랍니다. 감사합니다.",
        },
        {
            "prompt": "어제의 평균온도는 30도고 오늘의 평균온도는 20도야. 이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘",
            "rejected": "전광판에 표시할 메시지:\n\n\"오늘은 어제보다 시원해졌어요. 공원에서 산책을 즐기세요!\"\n\n이 메시지가 적절한가요?",
        },
    ]

    return bad_examples


def generate_good_examples_with_claude(bad_examples):
    """Claude API로 좋은 예시 생성"""
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    dpo_pairs = []

    for idx, bad_example in enumerate(bad_examples, 1):
        print(f"\n{idx}/{len(bad_examples)} 처리 중...")

        prompt = f"""당신은 공원 전광판 메시지 작성 전문가입니다.

다음은 나쁜 메시지 예시입니다:
```
{bad_example['rejected']}
```

**문제점:**
- 특수 토큰 (<think>, </think>)
- 불필요한 메타 설명 ("전광판에 표시할 메시지:")
- 질문 형식 ("이 메시지가 적절한가요?")
- 너무 장황함
- 온도 차이를 숫자로 명시하지 않음
- 관련 없는 정보 (날짜, 시간, 난방 등)

**요구사항:**
1. 40-70자 이내
2. 온도 차이를 숫자로 명시 (예: "10도 따뜻", "20도 상승")
3. "어제보다" 표현 사용
4. 특수문자, 이모지, 질문 금지
5. 한 문장으로 완결
6. 행동 권고 포함

**입력:**
{bad_example['prompt']}

위 입력에 대한 **완벽한 전광판 메시지**를 작성하세요.
메시지만 출력하고 다른 설명은 하지 마세요."""

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            chosen = response.content[0].text.strip()

            # 따옴표 제거
            chosen = chosen.strip('"').strip("'").strip()

            dpo_pairs.append({
                "prompt": bad_example['prompt'],
                "chosen": chosen,
                "rejected": bad_example['rejected']
            })

            print(f"  ✓ 생성 완료")
            print(f"    나쁜 예시: {bad_example['rejected'][:60]}...")
            print(f"    좋은 예시: {chosen}")

        except Exception as e:
            print(f"  ✗ 오류: {e}")
            continue

    return dpo_pairs


def generate_additional_scenarios():
    """추가 시나리오 생성 (더 많은 DPO 쌍)"""
    scenarios = []

    # 다양한 온도 변화
    temp_changes = [
        (-15, -14, "1도"),
        (-10, -5, "5도"),
        (-5, 5, "10도"),
        (0, 15, "15도"),
        (5, 25, "20도"),
        (10, -10, "20도"),
        (15, 10, "5도"),
        (20, 18, "2도"),
        (25, 10, "15도"),
        (30, 20, "10도"),
        (35, 25, "10도"),
    ]

    for yesterday, today, diff_desc in temp_changes:
        scenarios.append({
            "yesterday": yesterday,
            "today": today,
            "diff": today - yesterday
        })

    return scenarios


def generate_dpo_for_scenarios(scenarios):
    """시나리오에 대한 DPO 쌍 생성"""
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    dpo_pairs = []

    for idx, scenario in enumerate(scenarios, 1):
        print(f"\n시나리오 {idx}/{len(scenarios)} 처리 중...")

        prompt_text = f"어제의 평균온도는 {scenario['yesterday']}도고 오늘의 평균온도는 {scenario['today']}도야. " \
                      f"이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘"

        # Claude에게 좋은/나쁜 예시 모두 생성 요청
        request_prompt = f"""다음 입력에 대해 **좋은 메시지**와 **나쁜 메시지** 2개를 생성하세요.

입력: {prompt_text}

**좋은 메시지 요구사항:**
- 40-70자 이내
- 온도 차이 숫자로 명시
- "어제보다" 표현 사용
- 특수문자, 질문 금지
- 한 문장 완결

**나쁜 메시지 특징:**
- 특수 토큰 포함 (<think>)
- 메타 설명 ("전광판에 표시할 메시지:")
- 질문 형식
- 너무 장황함
- 온도 차이 미언급

JSON 형식으로 반환:
{{"chosen": "좋은 메시지", "rejected": "나쁜 메시지"}}

JSON만 반환하세요."""

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": request_prompt
                }]
            )

            content = response.content[0].text.strip()

            # JSON 추출
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            pair = json.loads(content)

            dpo_pairs.append({
                "prompt": prompt_text,
                "chosen": pair['chosen'],
                "rejected": pair['rejected']
            })

            print(f"  ✓ 생성 완료")

        except Exception as e:
            print(f"  ✗ 오류: {e}")
            continue

    return dpo_pairs


def save_dpo_dataset(dpo_pairs, output_path):
    """DPO 데이터셋 저장"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for pair in dpo_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + '\n')

    print(f"\n✓ DPO 데이터셋 저장 완료: {output_path}")
    print(f"✓ 총 {len(dpo_pairs)}쌍")


def print_samples(dpo_pairs, count=3):
    """샘플 출력"""
    print("\n" + "=" * 80)
    print("DPO 데이터셋 샘플")
    print("=" * 80)

    samples = random.sample(dpo_pairs, min(count, len(dpo_pairs)))

    for i, pair in enumerate(samples, 1):
        print(f"\n[쌍 {i}]")
        print(f"프롬프트: {pair['prompt'][:80]}...")
        print(f"\n✓ Chosen (좋은 예시):")
        print(f"  {pair['chosen']}")
        print(f"\n✗ Rejected (나쁜 예시):")
        print(f"  {pair['rejected'][:100]}...")


def main():
    print("=" * 80)
    print("DPO 데이터셋 생성 (Chosen/Rejected Pairs)")
    print("=" * 80)

    # API 키 확인
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY가 .env에 설정되지 않았습니다.")
        return

    all_dpo_pairs = []

    # 1. 기존 나쁜 예시에서 DPO 쌍 생성
    print("\n1️⃣ 기존 나쁜 예시로부터 DPO 쌍 생성 중...")
    bad_examples = load_current_model_outputs()
    dpo_pairs_1 = generate_good_examples_with_claude(bad_examples)
    all_dpo_pairs.extend(dpo_pairs_1)

    # 2. 추가 시나리오에서 DPO 쌍 생성
    print("\n2️⃣ 추가 시나리오에서 DPO 쌍 생성 중...")
    scenarios = generate_additional_scenarios()
    dpo_pairs_2 = generate_dpo_for_scenarios(scenarios)
    all_dpo_pairs.extend(dpo_pairs_2)

    if not all_dpo_pairs:
        print("\n⚠️  DPO 데이터셋 생성 실패")
        return

    # 3. 샘플 출력
    print_samples(all_dpo_pairs, count=5)

    # 4. 저장
    output_path = "data/dpo_dataset.jsonl"
    save_dpo_dataset(all_dpo_pairs, output_path)

    print("\n✓ 완료!")
    print("\n다음 단계:")
    print("1. DPO 학습 스크립트 실행")
    print("2. 학습된 모델로 테스트")
    print("3. Output cleaning 규칙 제거")


if __name__ == "__main__":
    main()
