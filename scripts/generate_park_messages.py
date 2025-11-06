"""
공원 전광판 메시지 대량 생성 스크립트
다양한 표현과 공원 특화 메시지 생성
"""

import json
import random
from pathlib import Path


# 공원 활동 및 시설
PARK_ACTIVITIES = [
    "산책", "조깅", "운동", "휴식", "사진 촬영", "피크닉",
    "자전거", "걷기", "달리기", "스트레칭", "명상"
]

PARK_FACILITIES = [
    "산책로", "벤치", "운동 시설", "쉼터", "정자", "광장",
    "분수대", "놀이터", "공원 입구", "산책길"
]

PARK_CONTEXTS = [
    "공원", "야외", "실외", "공원 방문", "공원 나들이"
]


def get_park_temperature_messages(yesterday: float, today: float) -> list:
    """
    온도 절대값과 변화량을 고려한 다양한 공원 메시지 생성
    각 온도 조건에 3-5개의 다양한 표현 반환
    """

    diff = abs(today - yesterday)
    is_increase = today > yesterday
    messages = []

    # ========== 온도 변화가 거의 없음 (±2도 이내) ==========
    if diff <= 2:
        if today >= 30:
            messages = [
                f"어제와 비슷하게 무덥습니다. 공원 분수대 근처에서 시원하게 쉬어가세요.",
                f"오늘도 더운 날씨가 이어집니다. 그늘에서 충분히 수분 섭취하세요.",
                f"날씨 변화 없이 무더운 하루입니다. 공원 벤치에서 휴식 권장합니다.",
                f"어제와 같은 폭염입니다. 야외 활동 시간을 줄여주세요.",
            ]
        elif today >= 22:
            messages = [
                f"어제와 비슷한 날씨입니다. 공원 산책하기 완벽한 하루예요.",
                f"날씨 변화 없이 화창합니다. 공원 나들이 즐겁게 하세요.",
                f"오늘도 쾌적한 날씨가 이어집니다. 산책로에서 여유를 즐기세요.",
                f"어제와 동일한 기온입니다. 공원 벤치에서 책 읽기 좋아요.",
                f"날씨가 안정적입니다. 야외 활동하기 완벽한 날입니다.",
            ]
        elif today >= 12:
            messages = [
                f"어제와 비슷한 날씨입니다. 공원 산책하며 가을을 즐기세요.",
                f"날씨 변화 없이 선선합니다. 운동하기 좋은 날씨예요.",
                f"오늘도 시원한 날씨가 이어집니다. 조깅 추천합니다.",
                f"어제와 같은 쾌적한 날입니다. 공원에서 여유로운 시간 보내세요.",
            ]
        elif today >= 5:
            messages = [
                f"어제와 비슷하게 쌀쌀합니다. 공원 산책 시 겉옷 챙기세요.",
                f"날씨 변화 없이 선선합니다. 따뜻하게 입고 산책 나오세요.",
                f"오늘도 서늘한 날씨입니다. 공원 벤치에 앉으실 때 주의하세요.",
            ]
        else:
            messages = [
                f"어제와 비슷하게 춥습니다. 짧은 산책 추천합니다.",
                f"날씨 변화 없이 추운 날입니다. 공원 방문 시 방한 철저히 하세요.",
                f"오늘도 한파가 이어집니다. 실내 운동 시설 이용을 권장합니다.",
            ]

    # ========== 온도 상승 ==========
    elif is_increase:
        if diff >= 15:  # 큰 상승
            if today >= 30:
                messages = [
                    f"어제보다 {diff:.0f}도 올라 매우 더워졌습니다. 공원 그늘에서 휴식하세요.",
                    f"급격히 {diff:.0f}도 상승해 무더워졌습니다. 야외 활동은 이른 아침 추천합니다.",
                    f"기온이 {diff:.0f}도나 올랐습니다. 공원 분수대 근처가 시원합니다.",
                    f"갑자기 {diff:.0f}도 더워졌습니다. 장시간 야외 활동은 자제해주세요.",
                ]
            elif today >= 22:
                messages = [
                    f"어제보다 {diff:.0f}도 올라 따뜻해졌습니다. 공원 산책 나들이 최고예요.",
                    f"급격히 {diff:.0f}도 상승해 포근합니다. 가벼운 옷차림으로 산책하세요.",
                    f"기온이 {diff:.0f}도 올라 봄 날씨입니다. 공원 곳곳에서 꽃구경 하세요.",
                    f"따뜻해진 날씨입니다. 공원 벤치에서 책 읽기 좋아요.",
                    f"{diff:.0f}도 상승으로 완벽한 산책 날씨입니다. 공원에서 즐거운 시간 보내세요.",
                ]
            elif today >= 12:
                messages = [
                    f"어제보다 {diff:.0f}도 올라 포근해졌습니다. 공원 조깅 추천합니다.",
                    f"기온이 {diff:.0f}도 상승했습니다. 운동하기 좋은 날씨예요.",
                    f"{diff:.0f}도 따뜻해져 야외 활동하기 좋습니다. 공원 산책로를 걸어보세요.",
                    f"날씨가 풀렸습니다. 공원에서 가족과 시간 보내기 좋아요.",
                ]
            else:
                messages = [
                    f"어제보다 {diff:.0f}도 올랐지만 쌀쌀합니다. 공원 방문 시 겉옷 필수예요.",
                    f"기온은 올랐으나 여전히 춥습니다. 따뜻하게 입고 산책하세요.",
                    f"{diff:.0f}도 상승했지만 추운 날씨입니다. 짧은 산책 추천합니다.",
                ]

        elif diff >= 7:  # 중간 상승
            if today >= 28:
                messages = [
                    f"어제보다 {diff:.0f}도 올라 더워졌습니다. 공원 그늘막 아래에서 쉬세요.",
                    f"{diff:.0f}도 상승해 무더워졌습니다. 오전 산책을 권장합니다.",
                    f"기온이 올라 더운 날입니다. 공원 분수 근처가 시원해요.",
                ]
            elif today >= 18:
                messages = [
                    f"어제보다 {diff:.0f}도 올라 따뜻합니다. 공원 산책 완벽한 날이에요.",
                    f"{diff:.0f}도 상승해 포근한 날씨입니다. 야외 활동 즐기세요.",
                    f"기온이 올라 쾌적합니다. 공원 벤치에서 여유 즐기세요.",
                    f"날씨가 좋아졌습니다. 공원 나들이 추천합니다.",
                    f"{diff:.0f}도 따뜻해진 날입니다. 공원 산책로를 걸어보세요.",
                ]
            else:
                messages = [
                    f"어제보다 {diff:.0f}도 올랐습니다. 공원 산책하기 좋아요.",
                    f"{diff:.0f}도 상승했지만 선선합니다. 조깅하기 좋은 날씨예요.",
                    f"기온이 올라 야외 활동하기 좋습니다. 공원을 걸어보세요.",
                ]

        else:  # 작은 상승 (3-6도)
            if today >= 28:
                messages = [
                    f"어제보다 {diff:.0f}도 올라 더 덥습니다. 공원 휴식 시 수분 섭취하세요.",
                    f"조금 더 더워진 날씨입니다. 그늘에서 산책하세요.",
                    f"{diff:.0f}도 상승한 무더운 날입니다. 공원 분수대를 찾아보세요.",
                ]
            elif today >= 18:
                messages = [
                    f"어제보다 {diff:.0f}도 올라 포근해졌습니다. 공원 산책 나가세요.",
                    f"조금 따뜻해진 날씨입니다. 공원에서 좋은 시간 보내세요.",
                    f"{diff:.0f}도 상승해 쾌적합니다. 야외 활동 즐기세요.",
                    f"날씨가 좋아졌습니다. 공원 벤치에서 휴식하세요.",
                    f"포근한 날입니다. 공원 산책로 추천합니다.",
                ]
            else:
                messages = [
                    f"어제보다 {diff:.0f}도 올랐습니다. 공원 산책하세요.",
                    f"조금 따뜻해졌습니다. 야외 활동하기 좋아요.",
                    f"{diff:.0f}도 상승한 날입니다. 공원을 걸어보세요.",
                ]

    # ========== 온도 하강 ==========
    else:
        if diff >= 15:  # 큰 하강
            if today >= 22:
                messages = [
                    f"어제보다 {diff:.0f}도 낮아져 시원해졌습니다. 공원 산책 최고예요.",
                    f"급격히 {diff:.0f}도 하강해 선선합니다. 야외 활동하기 완벽합니다.",
                    f"기온이 {diff:.0f}도나 떨어져 쾌적합니다. 공원 조깅 추천합니다.",
                    f"시원해진 날씨입니다. 공원에서 운동하기 좋아요.",
                ]
            elif today >= 12:
                messages = [
                    f"어제보다 {diff:.0f}도 낮아져 쌀쌀합니다. 공원 방문 시 겉옷 챙기세요.",
                    f"급격히 {diff:.0f}도 하강했습니다. 따뜻하게 입고 산책하세요.",
                    f"기온이 {diff:.0f}도 떨어졌습니다. 공원 산책 시 겉옷 필요해요.",
                    f"선선해진 날씨입니다. 긴팔 입고 공원 나오세요.",
                ]
            elif today >= 0:
                messages = [
                    f"어제보다 {diff:.0f}도 급락해 춥습니다. 공원 방문 시 따뜻하게 입으세요.",
                    f"갑자기 {diff:.0f}도 낮아져 추워졌습니다. 짧은 산책만 추천합니다.",
                    f"기온이 크게 떨어졌습니다. 공원 실내 시설 이용하세요.",
                ]
            else:
                messages = [
                    f"어제보다 {diff:.0f}도 급락해 매우 춥습니다. 공원 방문 자제 권장합니다.",
                    f"극심한 한파입니다. 실내 운동 시설을 이용하세요.",
                    f"위험한 추위입니다. 공원 야외 활동은 피해주세요.",
                ]

        elif diff >= 7:  # 중간 하강
            if today >= 22:
                messages = [
                    f"어제보다 {diff:.0f}도 낮아져 선선합니다. 공원 산책 완벽한 날씨예요.",
                    f"{diff:.0f}도 하강해 쾌적합니다. 야외 활동하기 최고입니다.",
                    f"시원해진 날씨입니다. 공원 조깅 추천합니다.",
                    f"기온이 내려가 좋은 날입니다. 공원에서 운동하세요.",
                ]
            elif today >= 12:
                messages = [
                    f"어제보다 {diff:.0f}도 낮아졌습니다. 공원 방문 시 가벼운 겉옷 챙기세요.",
                    f"{diff:.0f}도 하강해 쌀쌀합니다. 따뜻하게 입고 산책하세요.",
                    f"선선해진 날씨입니다. 공원 산책 시 긴팔 권장합니다.",
                    f"기온이 내려갔습니다. 공원 벤치는 쌀쌀할 수 있어요.",
                ]
            else:
                messages = [
                    f"어제보다 {diff:.0f}도 낮아져 춥습니다. 공원 방문 시 따뜻하게 입으세요.",
                    f"{diff:.0f}도 하강해 추워졌습니다. 두꺼운 옷 필수예요.",
                    f"추운 날씨입니다. 짧은 공원 산책만 추천합니다.",
                ]

        else:  # 작은 하강 (3-6도)
            if today >= 25:
                messages = [
                    f"어제보다 {diff:.0f}도 낮아져 선선합니다. 공원 산책 좋은 날씨예요.",
                    f"조금 시원해진 날입니다. 야외 활동 즐기세요.",
                    f"{diff:.0f}도 하강해 쾌적합니다. 공원에서 여유 즐기세요.",
                    f"선선해진 날씨입니다. 공원 조깅 추천합니다.",
                ]
            elif today >= 15:
                messages = [
                    f"어제보다 {diff:.0f}도 낮아졌습니다. 공원 산책하기 좋아요.",
                    f"조금 선선해졌습니다. 가벼운 겉옷 챙기세요.",
                    f"{diff:.0f}도 하강한 날입니다. 공원에서 운동하세요.",
                    f"선선한 날씨입니다. 공원 나들이 즐기세요.",
                ]
            elif today >= 5:
                messages = [
                    f"어제보다 {diff:.0f}도 낮아졌습니다. 공원 방문 시 겉옷 챙기세요.",
                    f"조금 쌀쌀해졌습니다. 따뜻하게 입고 산책하세요.",
                    f"{diff:.0f}도 하강했습니다. 공원 산책 시 긴팔 권장합니다.",
                ]
            else:
                messages = [
                    f"어제보다 {diff:.0f}도 낮아져 춥습니다. 공원 방문 시 따뜻하게 입으세요.",
                    f"조금 더 추워졌습니다. 두꺼운 옷 입고 나오세요.",
                    f"{diff:.0f}도 하강한 추운 날입니다. 짧은 산책 추천합니다.",
                ]

    return messages


def generate_temperature_variations_diverse():
    """다양한 온도 변화 패턴 생성 (500개 이상)"""

    data = []

    # 온도 범위: -20도 ~ 45도
    temp_range = list(range(-20, 46))

    # 각 온도 조합에 대해 여러 메시지 생성
    combinations = []

    # 1. 큰 변화 (±15도 이상): 100개
    for _ in range(50):
        yesterday = random.choice(temp_range)
        diff = random.randint(15, 25)
        today_up = yesterday + diff
        today_down = yesterday - diff

        if -20 <= today_up <= 45:
            combinations.append((yesterday, today_up))
        if -20 <= today_down <= 45:
            combinations.append((yesterday, today_down))

    # 2. 중간 변화 (±7-14도): 150개
    for _ in range(75):
        yesterday = random.choice(temp_range)
        diff = random.randint(7, 14)
        today_up = yesterday + diff
        today_down = yesterday - diff

        if -20 <= today_up <= 45:
            combinations.append((yesterday, today_up))
        if -20 <= today_down <= 45:
            combinations.append((yesterday, today_down))

    # 3. 작은 변화 (±3-6도): 200개
    for _ in range(100):
        yesterday = random.choice(temp_range)
        diff = random.randint(3, 6)
        today_up = yesterday + diff
        today_down = yesterday - diff

        if -20 <= today_up <= 45:
            combinations.append((yesterday, today_up))
        if -20 <= today_down <= 45:
            combinations.append((yesterday, today_down))

    # 4. 거의 변화 없음 (±0-2도): 100개
    for _ in range(50):
        yesterday = random.choice(temp_range)
        today = yesterday + random.choice([-2, -1, 0, 1, 2])

        if -20 <= today <= 45:
            combinations.append((yesterday, today))

    # 각 조합에 대해 메시지 생성
    for yesterday, today in combinations:
        messages = get_park_temperature_messages(yesterday, today)

        # 각 온도 조합에 여러 메시지 추가
        for msg in messages:
            input_text = f"어제 {yesterday}도, 오늘 {today}도"
            data.append({
                'input': input_text,
                'output': msg
            })

    return data


def generate_extreme_weather_park():
    """공원 특화 극한 날씨 메시지 (100개)"""

    scenarios = []

    # 폭염 - 공원 특화
    temps = list(range(35, 45))
    for temp in temps:
        scenarios.extend([
            {
                'input': f"폭염주의보, 현재 온도 {temp}도",
                'output': f"폭염주의보 발령, 기온 {temp}도입니다. 공원 그늘에서만 휴식하세요."
            },
            {
                'input': f"폭염주의보, 현재 온도 {temp}도",
                'output': f"기온 {temp}도로 매우 덥습니다. 공원 분수대 근처 이용 권장합니다."
            },
            {
                'input': f"폭염주의보, 현재 온도 {temp}도",
                'output': f"폭염 경보, {temp}도입니다. 공원 야외 활동은 이른 아침만 권장합니다."
            },
        ])

    # 한파 - 공원 특화
    temps = list(range(-20, -5))
    for temp in temps:
        scenarios.extend([
            {
                'input': f"한파경보, 현재 온도 {temp}도",
                'output': f"한파경보 발령, 기온 {temp}도입니다. 공원 실내 시설만 이용하세요."
            },
            {
                'input': f"한파경보, 현재 온도 {temp}도",
                'output': f"기온 {temp}도로 매우 춥습니다. 공원 방문은 자제해주세요."
            },
            {
                'input': f"한파경보, 현재 온도 {temp}도",
                'output': f"극한 한파 {temp}도입니다. 공원 산책로는 위험할 수 있습니다."
            },
        ])

    # 일교차 - 공원 특화
    for diff in range(10, 21):
        morning_temp = random.choice([0, 3, 5, 8, 10])
        afternoon_temp = morning_temp + diff
        scenarios.extend([
            {
                'input': f"일교차 {diff}도, 아침 {morning_temp}도 낮 {afternoon_temp}도",
                'output': f"일교차가 {diff}도로 큽니다. 공원 방문 시 겉옷 꼭 챙기세요."
            },
            {
                'input': f"일교차 {diff}도, 아침 {morning_temp}도 낮 {afternoon_temp}도",
                'output': f"아침 저녁 {diff}도 차이납니다. 공원 산책 시 체온 조절 주의하세요."
            },
        ])

    return scenarios[:100]  # 100개로 제한


def generate_weather_conditions_park():
    """공원 특화 날씨 조건 메시지 (50개)"""

    conditions = [
        # 비
        ("비 예보, 강수확률 80%", [
            "오늘 비 소식이 있습니다. 공원 방문 시 우산 꼭 챙기세요.",
            "비가 예상됩니다. 공원 실내 시설 이용을 권장합니다.",
            "강수 예보가 있습니다. 공원 산책로는 미끄러울 수 있어요.",
        ]),

        # 눈
        ("눈 예보, 적설량 5cm", [
            "오늘 눈이 내립니다. 공원 산책로 미끄러움 주의하세요.",
            "적설이 예상됩니다. 공원 방문 시 미끄럼 방지 신발 착용하세요.",
            "눈 소식이 있습니다. 공원 야외 활동 주의 필요합니다.",
        ]),

        # 강풍
        ("강풍주의보, 초속 15m", [
            "바람이 강하게 붑니다. 공원 산책 시 주의하세요.",
            "강풍 주의보입니다. 공원 나무 아래는 피해주세요.",
            "바람이 세게 붑니다. 공원 실내 시설 이용 권장합니다.",
        ]),

        # 황사
        ("황사경보 발령", [
            "황사가 발생했습니다. 공원 방문 시 마스크 착용하세요.",
            "황사 농도가 높습니다. 공원 야외 활동 자제 권장합니다.",
            "황사 경보입니다. 공원 실내 시설을 이용하세요.",
        ]),

        # 미세먼지
        ("미세먼지 매우나쁨", [
            "미세먼지 농도가 매우 나쁩니다. 공원 방문 시 마스크 필수예요.",
            "공기질이 나쁩니다. 공원 야외 활동은 자제해주세요.",
            "미세먼지 경보입니다. 공원 실내 운동 시설을 이용하세요.",
        ]),

        # 안개
        ("안개주의보", [
            "짙은 안개로 시야가 불량합니다. 공원 산책 시 주의하세요.",
            "안개 주의보입니다. 공원 내 이동 시 조심하세요.",
            "시야가 좋지 않습니다. 공원 방문 시 천천히 이동하세요.",
        ]),
    ]

    scenarios = []
    for input_text, outputs in conditions:
        for output_text in outputs:
            # 각 메시지를 3번씩 반복
            for _ in range(3):
                scenarios.append({
                    'input': input_text,
                    'output': output_text
                })

    return scenarios[:50]  # 50개로 제한


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
    print("공원 특화 대량 학습 데이터 생성")
    print("=" * 70)

    # 데이터 생성
    print("\n1. 온도 변화 패턴 생성 중... (500개 이상, 다양한 표현)")
    temp_data = generate_temperature_variations_diverse()
    print(f"   생성 완료: {len(temp_data)}개")

    print("\n2. 공원 특화 극한 날씨 생성 중... (100개)")
    extreme_data = generate_extreme_weather_park()
    print(f"   생성 완료: {len(extreme_data)}개")

    print("\n3. 공원 특화 날씨 조건 생성 중... (50개)")
    weather_data = generate_weather_conditions_park()
    print(f"   생성 완료: {len(weather_data)}개")

    # 전체 데이터 합치기
    all_data = temp_data + extreme_data + weather_data

    # 중복 제거 (입력만 같고 출력이 다른 경우는 유지)
    unique_data = []
    seen = {}
    for item in all_data:
        key = f"{item['input']}||{item['output']}"
        if key not in seen:
            seen[key] = True
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

    train_file = data_dir / "train_park.jsonl"
    val_file = data_dir / "validation_park.jsonl"

    print(f"\n6. 파일 저장 중...")

    with open(train_file, 'w', encoding='utf-8') as f:
        for item in train_structured:
            f.write(json.dumps({"text": item["text"]}, ensure_ascii=False) + '\n')

    with open(val_file, 'w', encoding='utf-8') as f:
        for item in val_structured:
            f.write(json.dumps({"text": item["text"]}, ensure_ascii=False) + '\n')

    print(f"   ✓ 학습 데이터: {train_file}")
    print(f"   ✓ 검증 데이터: {val_file}")

    # 샘플 출력 (다양성 확인)
    print("\n" + "=" * 70)
    print("생성된 데이터 샘플 (다양성 확인):")
    print("=" * 70)

    # 같은 온도 조건에 다양한 표현 확인
    test_input = "어제 25도, 오늘 15도"
    matching = [d for d in train_data if d['input'] == test_input]

    print(f"\n입력: {test_input}")
    print(f"생성된 다양한 표현 ({len(matching)}개):")
    for i, item in enumerate(matching[:5], 1):
        print(f"  {i}. {item['output']}")

    print("\n" + "=" * 70)
    print("✅ 공원 특화 대량 데이터 생성 완료!")
    print("=" * 70)
    print("\n다음 단계:")
    print("  python scripts/finetune_model_park.py")


if __name__ == "__main__":
    main()
