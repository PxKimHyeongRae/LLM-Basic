"""
합성 학습 데이터 생성 스크립트
OpenRouter API를 사용하여 전광판 메시지 학습 데이터를 자동 생성합니다.
"""

import os
import json
import random
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# OpenRouter 클라이언트 설정
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY'),
)

def generate_message_pair(scenario: str, context: Dict) -> Dict:
    """
    주어진 시나리오와 컨텍스트를 바탕으로 입력-출력 쌍을 생성합니다.
    """
    prompt = f"""당신은 야외 공원 전광판 메시지 작성 전문가입니다.

시나리오: {scenario}
컨텍스트: {json.dumps(context, ensure_ascii=False)}

위 시나리오에 대해 다음을 생성하세요:
1. 사용자 입력 (input): 간단한 메모나 센서 데이터 설명 (10-30자)
2. 전광판 출력 (output): 공원 시민들에게 보낼 친근하고 명확한 안내 메시지 (40-70자)

규칙:
- 존댓말 사용 (～요, ～세요)
- 공공의 이익을 위한 내용
- 구체적이고 실용적인 조언
- 부정적 표현보다는 긍정적 제안

JSON 형식으로만 답변하세요:
{{"input": "...", "output": "..."}}
"""

    try:
        completion = client.chat.completions.create(
            extra_body={},
            model=os.getenv('OPENROUTER_MODEL', 'tngtech/deepseek-r1t2-chimera:free'),
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = completion.choices[0].message.content.strip()

        # JSON 추출 (코드 블록 제거)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        data = json.loads(response_text)
        return data

    except Exception as e:
        print(f"Error generating pair: {e}")
        return None


def create_scenarios() -> List[tuple]:
    """
    다양한 시나리오와 컨텍스트를 생성합니다.
    """
    scenarios = []

    # 1. 온도 기반 시나리오 (30개)
    temperatures = [
        (35, 45, "폭염"), (30, 40, "더위"), (25, 30, "따뜻함"),
        (20, 25, "쾌적함"), (15, 20, "선선함"), (10, 15, "쌀쌀함"),
        (5, 10, "추위"), (0, 5, "강추위"), (-5, 0, "혹한")
    ]

    for temp_min, temp_max, condition in temperatures:
        for i in range(3):
            temp = random.randint(temp_min, temp_max)
            scenarios.append((
                f"온도 {temp}°C - {condition} 상황",
                {"temperature": temp, "condition": condition, "location": "공원"}
            ))

    # 2. 습도 기반 시나리오 (20개)
    humidity_ranges = [
        (80, 95, "매우 습함"), (70, 80, "습함"),
        (40, 60, "쾌적"), (20, 40, "건조"), (10, 20, "매우 건조")
    ]

    for hum_min, hum_max, condition in humidity_ranges:
        for i in range(4):
            humidity = random.randint(hum_min, hum_max)
            scenarios.append((
                f"습도 {humidity}% - {condition} 상황",
                {"humidity": humidity, "condition": condition, "location": "공원"}
            ))

    # 3. 온도+습도 복합 시나리오 (20개)
    combined_scenarios = [
        (32, 75, "무더위"), (28, 85, "찜통더위"), (5, 80, "습한 추위"),
        (15, 30, "건조한 날씨"), (-2, 60, "한파")
    ]

    for temp, humidity, condition in combined_scenarios:
        for i in range(4):
            scenarios.append((
                f"온도 {temp}°C, 습도 {humidity}% - {condition}",
                {"temperature": temp, "humidity": humidity, "condition": condition}
            ))

    # 4. 변위계 이상 시나리오 (15개)
    displacement_scenarios = [
        "X축 각도 이상 감지", "Y축 각도 이상 감지", "변위계 기울기 감지",
        "시설물 점검 필요", "구조물 모니터링 중"
    ]

    for scenario in displacement_scenarios:
        for i in range(3):
            x_angle = random.uniform(-5, 5)
            y_angle = random.uniform(-5, 5)
            scenarios.append((
                scenario,
                {"x_angle": round(x_angle, 2), "y_angle": round(y_angle, 2),
                 "alert_type": "안전점검"}
            ))

    # 5. 일반 공원 안내 시나리오 (30개)
    general_scenarios = [
        ("쓰레기 분리수거 안내", {"category": "환경"}),
        ("반려동물 동반 안내", {"category": "이용수칙"}),
        ("흡연 구역 안내", {"category": "이용수칙"}),
        ("운동기구 이용 안내", {"category": "시설"}),
        ("화장실 위치 안내", {"category": "편의시설"}),
        ("음수대 이용 안내", {"category": "편의시설"}),
        ("야간 운영시간 안내", {"category": "운영"}),
        ("우천 시 주의사항", {"category": "안전"}),
        ("미끄럼 주의", {"category": "안전"}),
        ("낙상 주의", {"category": "안전"}),
    ]

    for scenario, context in general_scenarios:
        for i in range(3):
            scenarios.append((scenario, context))

    # 6. 계절별 특화 시나리오 (20개)
    seasonal_scenarios = [
        ("봄철 황사 주의", {"season": "봄", "issue": "황사"}),
        ("여름 폭염 대비", {"season": "여름", "issue": "폭염"}),
        ("가을 낙엽 청소", {"season": "가을", "issue": "환경"}),
        ("겨울 빙판 주의", {"season": "겨울", "issue": "안전"}),
        ("장마철 대비", {"season": "여름", "issue": "강수"}),
    ]

    for scenario, context in seasonal_scenarios:
        for i in range(4):
            scenarios.append((scenario, context))

    # 7. 긴급/재난 안내 시나리오 (15개)
    emergency_scenarios = [
        ("미세먼지 나쁨", {"pm10": 120, "level": "나쁨"}),
        ("초미세먼지 매우나쁨", {"pm2.5": 80, "level": "매우나쁨"}),
        ("오존 경보", {"o3": 0.15, "level": "경보"}),
        ("폭염 경보", {"temperature": 38, "level": "경보"}),
        ("한파 주의보", {"temperature": -10, "level": "주의보"}),
    ]

    for scenario, context in emergency_scenarios:
        for i in range(3):
            scenarios.append((scenario, context))

    return scenarios


def generate_dataset(num_samples: int = 150, output_file: str = "data/training_data.jsonl"):
    """
    학습 데이터셋을 생성합니다.
    """
    print(f"총 {num_samples}개의 학습 데이터를 생성합니다...")

    # 시나리오 생성
    all_scenarios = create_scenarios()

    # 랜덤하게 섞기
    random.shuffle(all_scenarios)

    # 필요한 만큼만 선택
    selected_scenarios = all_scenarios[:num_samples]

    # 데이터 생성
    dataset = []

    for scenario, context in tqdm(selected_scenarios, desc="데이터 생성 중"):
        pair = generate_message_pair(scenario, context)

        if pair and "input" in pair and "output" in pair:
            dataset.append(pair)
        else:
            print(f"실패한 시나리오: {scenario}")

    # 파일 저장
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"\n✅ {len(dataset)}개의 데이터가 {output_file}에 저장되었습니다.")

    # 샘플 출력
    print("\n📋 생성된 데이터 샘플:")
    for i, item in enumerate(dataset[:5], 1):
        print(f"\n{i}.")
        print(f"  입력: {item['input']}")
        print(f"  출력: {item['output']}")


def split_dataset(input_file: str = "data/training_data.jsonl",
                  train_ratio: float = 0.9):
    """
    데이터셋을 학습/검증 세트로 분할합니다.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    random.shuffle(data)

    split_idx = int(len(data) * train_ratio)
    train_data = data[:split_idx]
    val_data = data[split_idx:]

    # 저장
    with open('data/train.jsonl', 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    with open('data/validation.jsonl', 'w', encoding='utf-8') as f:
        for item in val_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"\n✅ 데이터 분할 완료:")
    print(f"  - 학습 데이터: {len(train_data)}개 → data/train.jsonl")
    print(f"  - 검증 데이터: {len(val_data)}개 → data/validation.jsonl")


if __name__ == "__main__":
    # 1. 학습 데이터 생성 (150개)
    generate_dataset(num_samples=150)

    # 2. 학습/검증 분할
    split_dataset()
