"""
Chat 형식 파인튜닝 데이터 생성
KORMo 모델의 대화 형식에 최적화된 구조
wrap_temperature_data.py의 340개 데이터를 모두 Chat 형식으로 변환
"""

import json
import sys
import os

# wrap_temperature_data.py에서 데이터 가져오기
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from wrap_temperature_data import TRAIN_DATA as LARGE_TRAIN_DATA
from wrap_temperature_data import VALIDATION_DATA as LARGE_VAL_DATA


# 시스템 프롬프트 (간결하게)
SYSTEM_PROMPT = "당신은 공원 전광판 메시지 전문가입니다. 온도 정보를 받아 40-70자 길이의 간결한 한 문장 메시지를 작성하세요. 온도 차이를 구체적 숫자로 명시하고 공원 관련 조언을 포함하세요."


def create_chat_format(yesterday, today, message):
    """Chat 형식으로 데이터 변환"""
    user_message = f"어제 {yesterday}도, 오늘 {today}도"

    # KORMo 모델의 chat 템플릿 형식
    text = f"""<|im_start|>system
{SYSTEM_PROMPT}<|im_end|>
<|im_start|>user
{user_message}<|im_end|>
<|im_start|>assistant
{message}<|im_end|>"""

    return text


# wrap_temperature_data.py에서 가져온 대량 데이터 사용
TRAIN_DATA = LARGE_TRAIN_DATA  # 340개
VALIDATION_DATA = LARGE_VAL_DATA  # 15개


def create_jsonl(data, output_file):
    """데이터를 JSONL 형식으로 저장"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for yesterday, today, message in data:
            text = create_chat_format(yesterday, today, message)
            f.write(json.dumps({"text": text}, ensure_ascii=False) + '\n')


def main():
    print("=" * 70)
    print("Chat 형식 학습 데이터 생성 (대량 데이터)")
    print("=" * 70)
    print(f"\n[데이터 로드] wrap_temperature_data.py에서 {len(LARGE_TRAIN_DATA)}개 학습 데이터 로드")
    print(f"[데이터 로드] wrap_temperature_data.py에서 {len(LARGE_VAL_DATA)}개 검증 데이터 로드")

    # 학습 데이터 생성
    train_file = "data/train_chat_large.jsonl"
    create_jsonl(TRAIN_DATA, train_file)
    print(f"\n[OK] 학습 데이터: {len(TRAIN_DATA)}개 -> {train_file}")

    # 검증 데이터 생성
    val_file = "data/validation_chat_large.jsonl"
    create_jsonl(VALIDATION_DATA, val_file)
    print(f"[OK] 검증 데이터: {len(VALIDATION_DATA)}개 -> {val_file}")

    # 샘플 출력
    print("\n" + "=" * 70)
    print("Chat 형식 예시 (첫 3개):")
    print("=" * 70)
    for i in range(min(3, len(TRAIN_DATA))):
        yesterday, today, message = TRAIN_DATA[i]
        print(f"\n[샘플 {i+1}] 어제 {yesterday}도, 오늘 {today}도")
        print(f"메시지: {message}")

    print("\n" + "=" * 70)
    print("Inference 시 사용할 프롬프트 형식:")
    print("=" * 70)
    inference = f"""<|im_start|>system
{SYSTEM_PROMPT}<|im_end|>
<|im_start|>user
어제 10도, 오늘 20도<|im_end|>
<|im_start|>assistant
"""
    print(inference)
    print("[여기서 모델이 메시지를 생성함]")

    print("\n" + "=" * 70)
    print("[완료] 대량 데이터 생성 완료!")
    print(f"   총 {len(TRAIN_DATA) + len(VALIDATION_DATA)}개의 데이터가 생성되었습니다.")
    print("=" * 70)

    print("\n[다음 단계]")
    print("1. finetune_model_temperature.py 수정:")
    print(f"   TRAIN_FILE = '{train_file}'")
    print(f"   VAL_FILE = '{val_file}'")
    print("   OUTPUT_DIR = './finetuned_model_chat_large'")
    print("\n2. 파인튜닝 실행:")
    print("   python scripts/finetune_model_temperature.py")
    print("\n3. .env 설정:")
    print("   USE_FINETUNED=true")
    print("   ADAPTER_PATH=./finetuned_model_chat_large")
    print("   USE_CHAT_FORMAT=true")


if __name__ == "__main__":
    main()
