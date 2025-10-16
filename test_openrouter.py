"""
OpenRouter API 서버 테스트 (간단 버전)
"""

import requests


def test():
    """기본 테스트"""
    print("=" * 70)
    print("OpenRouter API 테스트 (포트 8002)")
    print("=" * 70)

    # 1. 서버 상태 확인
    print("\n1. 서버 상태 확인...")
    try:
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 서버 상태: {data['status']}")
            print(f"  API 키: {'설정됨' if data['api_key_set'] else '없음'}")

            if not data['api_key_set']:
                print("\n⚠️ .env에 OPENROUTER_API_KEY를 설정하세요")
                return
        else:
            print(f"✗ 오류: {response.status_code}")
            return

    except requests.exceptions.ConnectionError:
        print("✗ 서버 연결 실패!")
        print("먼저 서버를 시작하세요: python openrouter_server.py")
        return

    # 2. 텍스트 생성 테스트
    print("\n2. 텍스트 생성 테스트...")

    prompt = "어제의 평균온도는 18도고 오늘의 평균온도는 24도야. 이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘 (100자 이내)"

    print(f"\n프롬프트:\n{prompt}")
    print("\n생성 중...\n")

    try:
        response = requests.post(
            "http://localhost:8002/generate",
            json={"prompt": prompt},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            print("=" * 70)
            print("AI 응답:")
            print(result['generated_text'])
            print("=" * 70)
            print(f"\n모델: {result['model']}")
            print(f"소요 시간: {result['generation_time']:.2f}초")

        else:
            print(f"✗ 오류 {response.status_code}:")
            print(response.text)

    except Exception as e:
        print(f"✗ 오류: {e}")


def test_custom():
    """사용자 정의 프롬프트"""
    print("\n" + "=" * 70)
    print("사용자 정의 프롬프트 테스트")
    print("=" * 70)

    prompt = input("\n프롬프트를 입력하세요: ").strip()

    if not prompt:
        print("프롬프트가 비어있습니다.")
        return

    print("\n생성 중...\n")

    try:
        response = requests.post(
            "http://localhost:8002/generate",
            json={"prompt": prompt},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            print("=" * 70)
            print("AI 응답:")
            print(result['generated_text'])
            print("=" * 70)
            print(f"\n소요 시간: {result['generation_time']:.2f}초")
        else:
            print(f"✗ 오류: {response.status_code}")

    except Exception as e:
        print(f"✗ 오류: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "custom":
        test_custom()
    else:
        test()

        print("\n" + "=" * 70)
        choice = input("\n사용자 정의 프롬프트를 테스트하시겠습니까? (y/n): ")
        if choice.lower() == 'y':
            test_custom()
