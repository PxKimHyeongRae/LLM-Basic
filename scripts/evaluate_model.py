"""
파인튜닝된 모델 평가 스크립트
원본 모델과 파인튜닝 모델의 성능을 비교합니다.
"""

import os
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from dotenv import load_dotenv

load_dotenv()


def load_finetuned_model(base_model_name: str, adapter_path: str):
    """
    파인튜닝된 모델을 로드합니다.
    """
    print(f"📦 파인튜닝된 모델 로드 중...")

    # 양자화 설정
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,
        bnb_8bit_compute_dtype=torch.float16,
    )

    # 베이스 모델 로드
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )

    # LoRA 어댑터 적용
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()

    # 토크나이저 로드
    tokenizer = AutoTokenizer.from_pretrained(
        adapter_path,
        trust_remote_code=True,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("✅ 모델 로드 완료")
    return model, tokenizer


def generate_message(model, tokenizer, user_input: str, max_length: int = 150) -> str:
    """
    모델을 사용하여 메시지를 생성합니다.
    """
    prompt = f"""아래 입력을 공원 전광판에 표시할 메시지로 변환하세요.

입력: {user_input}
출력:"""

    inputs = tokenizer(prompt, return_tensors="pt", padding=True).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # "출력:" 이후 텍스트만 추출
    if "출력:" in generated_text:
        result = generated_text.split("출력:")[1].strip()
        # 다음 줄이나 특수 문자 제거
        result = result.split('\n')[0].strip()
        return result
    else:
        return generated_text


def evaluate_on_test_cases(model, tokenizer):
    """
    테스트 케이스로 모델을 평가합니다.
    """
    test_cases = [
        "온도 35도 폭염",
        "습도 85% 찜통더위",
        "변위계 이상 감지",
        "미세먼지 나쁨",
        "쓰레기 분리수거",
        "반려동물 동반 주의",
        "겨울 빙판길 주의",
        "여름 물 섭취 권장",
        "어린이 놀이터 안전",
        "야간 운영시간 안내",
    ]

    print("\n" + "="*60)
    print("📋 테스트 케이스 평가")
    print("="*60)

    for i, test_input in enumerate(test_cases, 1):
        output = generate_message(model, tokenizer, test_input)
        print(f"\n[{i}] 입력: {test_input}")
        print(f"    출력: {output}")
        print(f"    길이: {len(output)}자")


def evaluate_on_validation_data(model, tokenizer, val_file: str = "data/validation.jsonl"):
    """
    검증 데이터로 모델을 평가합니다.
    """
    if not os.path.exists(val_file):
        print(f"\n⚠️  검증 파일이 없습니다: {val_file}")
        return

    with open(val_file, 'r', encoding='utf-8') as f:
        val_data = [json.loads(line) for line in f]

    print("\n" + "="*60)
    print("📊 검증 데이터 평가 (5개 샘플)")
    print("="*60)

    for i, sample in enumerate(val_data[:5], 1):
        user_input = sample['input']
        expected_output = sample['output']
        generated_output = generate_message(model, tokenizer, user_input)

        print(f"\n[{i}] 입력: {user_input}")
        print(f"    정답: {expected_output}")
        print(f"    생성: {generated_output}")
        print(f"    길이: {len(generated_output)}자")


def interactive_test(model, tokenizer):
    """
    대화형 테스트 모드
    """
    print("\n" + "="*60)
    print("💬 대화형 테스트 모드 (종료: 'q' 입력)")
    print("="*60)

    while True:
        user_input = input("\n입력: ").strip()

        if user_input.lower() in ['q', 'quit', 'exit']:
            print("테스트를 종료합니다.")
            break

        if not user_input:
            continue

        output = generate_message(model, tokenizer, user_input)
        print(f"출력: {output}")
        print(f"길이: {len(output)}자")


def main():
    BASE_MODEL = os.getenv('MODEL_NAME', 'KORMo-Team/KORMo-10B-sft')
    ADAPTER_PATH = "./finetuned_model"

    if not os.path.exists(ADAPTER_PATH):
        print(f"❌ 파인튜닝된 모델이 없습니다: {ADAPTER_PATH}")
        print("먼저 finetune_model.py를 실행하세요.")
        return

    # 모델 로드
    model, tokenizer = load_finetuned_model(BASE_MODEL, ADAPTER_PATH)

    # 평가 실행
    evaluate_on_test_cases(model, tokenizer)
    evaluate_on_validation_data(model, tokenizer)

    # 대화형 테스트 (선택 사항)
    choice = input("\n대화형 테스트를 시작하시겠습니까? (y/n): ").strip().lower()
    if choice == 'y':
        interactive_test(model, tokenizer)


if __name__ == "__main__":
    main()
