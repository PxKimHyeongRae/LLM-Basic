"""
Claude API를 사용하여 고품질 학습 데이터 생성 (규칙 없이)

목표:
- if/else 없이 자연스러운 메시지 생성
- Claude가 다양한 표현 생성
- 500개 온도 시나리오
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


def generate_temperature_scenarios():
    """온도 시나리오 생성 (규칙 없이, 다양성 확보)"""
    scenarios = []

    # 기본 온도 범위
    base_temps = list(range(-20, 41, 5))  # -20, -15, ..., 35, 40

    for base in base_temps:
        # 각 기준 온도에서 다양한 변화 생성
        changes = list(range(-30, 31, 2))  # -30, -28, ..., 28, 30

        for change in changes:
            today = base + change
            # 현실적인 온도 범위만
            if -25 <= today <= 45:
                scenarios.append({
                    'yesterday': base,
                    'today': today,
                    'diff': change
                })

    # 중복 제거
    unique_scenarios = []
    seen = set()
    for s in scenarios:
        key = (s['yesterday'], s['today'])
        if key not in seen:
            seen.add(key)
            unique_scenarios.append(s)

    print(f"총 {len(unique_scenarios)}개 시나리오 생성")
    return unique_scenarios[:500]  # 최대 500개


def generate_messages_with_claude(scenarios, batch_size=50):
    """Claude API로 메시지 생성 (배치 처리)"""
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    all_data = []
    total_batches = (len(scenarios) + batch_size - 1) // batch_size

    for batch_idx in range(0, len(scenarios), batch_size):
        batch = scenarios[batch_idx:batch_idx + batch_size]
        batch_num = batch_idx // batch_size + 1

        print(f"\n배치 {batch_num}/{total_batches} 처리 중 ({len(batch)}개)...")

        # Claude에게 요청
        prompt = f"""당신은 공원 전광판 메시지 작성 전문가입니다.

다음 온도 변화 시나리오에 대해 전광판 메시지를 생성하세요.

**요구사항:**
1. 각 메시지는 40-70자 이내
2. 온도 차이를 숫자로 명시 (예: "10도 따뜻", "5도 추움", "20도 상승")
3. "어제보다" 표현 사용
4. 특수문자, 이모지, 질문 금지
5. 자연스러운 한국어, 완결된 한 문장
6. 행동 권고 포함 (옷차림, 수분 섭취 등)

**스타일 가이드:**
- 친근하고 따뜻한 톤
- 시민 안전 우선
- 구체적이고 실용적인 조언

**온도 변화에 따른 표현 다양화:**
- 작은 변화 (1-3도): "약간", "조금"
- 중간 변화 (4-9도): "상당히", "꽤"
- 큰 변화 (10-19도): "많이", "매우"
- 극단적 변화 (20도 이상): "급격히", "크게"

**시나리오:**
{json.dumps(batch, ensure_ascii=False, indent=2)}

각 시나리오에 대해 하나의 메시지를 생성하고, 다음 JSON 형식으로 반환하세요:
[
  {{"yesterday": -15, "today": -10, "message": "어제보다 5도 따뜻해졌습니다. 산책하기 좋은 날씨예요."}},
  ...
]

JSON만 반환하고 다른 설명은 하지 마세요."""

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # 응답 파싱
            content = response.content[0].text.strip()

            # JSON 추출 (```json ... ``` 제거)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            batch_data = json.loads(content)
            all_data.extend(batch_data)

            print(f"  ✓ {len(batch_data)}개 메시지 생성 완료")

        except Exception as e:
            print(f"  ✗ 오류 발생: {e}")
            # 실패한 배치는 건너뛰기
            continue

    return all_data


def save_to_jsonl(data, output_path):
    """JSONL 형식으로 저장"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            # 학습 데이터 형식으로 변환
            training_item = {
                "input": f"어제의 평균온도는 {item['yesterday']}도고 오늘의 평균온도는 {item['today']}도야. "
                         f"이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘",
                "output": item['message']
            }
            f.write(json.dumps(training_item, ensure_ascii=False) + '\n')

    print(f"\n✓ 저장 완료: {output_path}")
    print(f"✓ 총 {len(data)}개 데이터")


def print_samples(data, count=5):
    """샘플 출력"""
    print("\n" + "=" * 80)
    print("생성된 메시지 샘플")
    print("=" * 80)

    import random
    samples = random.sample(data, min(count, len(data)))

    for i, sample in enumerate(samples, 1):
        diff = sample['today'] - sample['yesterday']
        print(f"\n[샘플 {i}]")
        print(f"  어제: {sample['yesterday']}도, 오늘: {sample['today']}도 (차이: {diff:+d}도)")
        print(f"  메시지: {sample['message']}")
        print(f"  길이: {len(sample['message'])}자")


def main():
    print("=" * 80)
    print("Claude 기반 학습 데이터 생성 (규칙 없이)")
    print("=" * 80)

    # API 키 확인
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY가 .env에 설정되지 않았습니다.")
        print("https://console.anthropic.com/에서 API 키를 발급받아 .env에 추가하세요:")
        print("ANTHROPIC_API_KEY=sk-ant-...")
        return

    # 1. 시나리오 생성
    print("\n1️⃣ 온도 시나리오 생성 중...")
    scenarios = generate_temperature_scenarios()

    # 2. Claude로 메시지 생성
    print("\n2️⃣ Claude API로 메시지 생성 중...")
    print("(배치 처리로 진행, 약 5-10분 소요)")
    data = generate_messages_with_claude(scenarios, batch_size=50)

    if not data:
        print("\n⚠️  데이터 생성 실패")
        return

    # 3. 샘플 출력
    print_samples(data, count=10)

    # 4. 저장
    output_path = "data/training_data_claude.jsonl"
    save_to_jsonl(data, output_path)

    print("\n✓ 완료!")
    print("\n다음 단계:")
    print("1. DPO 데이터셋 생성 (chosen/rejected pairs)")
    print("2. DPO 학습 실행")
    print("3. Output cleaning 규칙 제거 및 프롬프트로 대체")


if __name__ == "__main__":
    main()
