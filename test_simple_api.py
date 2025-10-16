"""
간단한 API 테스트 - 프롬프트만 넣으면 AI가 응답
"""

import requests
import json


def test_simple_prompt():
    """간단한 프롬프트 테스트"""

    # API 엔드포인트
    url = "http://localhost:8000/generate"

    # 예시 프롬프트
    prompt = """어제의 평균온도는 18도고 오늘의 평균온도는 24도야.
이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 메시지를 작성해줘"""

    # 요청 데이터
    data = {
        "prompt": prompt,
        "max_new_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "repetition_penalty": 1.2
    }

    print("=" * 70)
    print("프롬프트:")
    print(prompt)
    print("=" * 70)
    print("\n생성 중...\n")

    try:
        # API 호출
        response = requests.post(url, json=data, timeout=120)

        if response.status_code == 200:
            result = response.json()

            print("=" * 70)
            print("AI 응답:")
            print(result['generated_text'])
            print("=" * 70)
            print(f"\n소요 시간: {result['generation_time']:.2f}초")

        else:
            print(f"오류 발생: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패!")
        print("다음 명령으로 서버를 먼저 시작하세요:")
        print("  python model_server.py")

    except Exception as e:
        print(f"오류: {e}")


def test_multiple_prompts():
    """여러 프롬프트 테스트"""

    url = "http://localhost:8000/generate"

    prompts = [
        "어제의 평균온도는 18도고 오늘의 평균온도는 24도야. 공원을 방문하는 고객들에게 적절하게 전달해줄 메시지를 작성해줘",
        "오늘 일교차가 15도로 매우 큽니다. 시민들에게 건강 조언을 해주세요",
        "내일 비가 올 예정입니다. 등산객들에게 안전 메시지를 작성해주세요",
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'=' * 70}")
        print(f"테스트 {i}/{len(prompts)}")
        print(f"{'=' * 70}")
        print(f"프롬프트: {prompt}")
        print()

        try:
            response = requests.post(
                url,
                json={
                    "prompt": prompt,
                    "max_new_tokens": 80,
                    "temperature": 0.6
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                print(f"응답: {result['generated_text']}")
                print(f"소요 시간: {result['generation_time']:.2f}초")
            else:
                print(f"오류: {response.status_code}")

        except Exception as e:
            print(f"오류: {e}")
            break


def test_custom_prompt():
    """사용자 정의 프롬프트 테스트"""

    print("\n" + "=" * 70)
    print("사용자 정의 프롬프트 테스트")
    print("=" * 70)

    # 사용자로부터 프롬프트 입력
    print("\n프롬프트를 입력하세요 (엔터 2번으로 종료):")
    lines = []
    while True:
        line = input()
        if line == "":
            if lines and lines[-1] == "":
                break
        lines.append(line)

    prompt = "\n".join(lines[:-1])  # 마지막 빈 줄 제거

    if not prompt.strip():
        print("프롬프트가 비어있습니다.")
        return

    url = "http://localhost:8000/generate"

    print("\n생성 중...")

    try:
        response = requests.post(
            url,
            json={
                "prompt": prompt,
                "max_new_tokens": 100,
                "temperature": 0.7
            },
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 70)
            print("AI 응답:")
            print(result['generated_text'])
            print("=" * 70)
            print(f"\n소요 시간: {result['generation_time']:.2f}초")
        else:
            print(f"오류: {response.status_code}")

    except Exception as e:
        print(f"오류: {e}")


if __name__ == "__main__":
    import sys

    print("\n🌡️ KORMo AI 모델 API 테스트")
    print("=" * 70)

    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("\n테스트 모드 선택:")
        print("  1. 단일 프롬프트 테스트")
        print("  2. 여러 프롬프트 테스트")
        print("  3. 사용자 정의 프롬프트")
        print()
        mode = input("선택 (1-3): ").strip()

    if mode == "1":
        test_simple_prompt()
    elif mode == "2":
        test_multiple_prompts()
    elif mode == "3":
        test_custom_prompt()
    else:
        print("잘못된 선택입니다.")
        print("\n사용법:")
        print("  python test_simple_api.py 1  # 단일 프롬프트")
        print("  python test_simple_api.py 2  # 여러 프롬프트")
        print("  python test_simple_api.py 3  # 사용자 정의")
