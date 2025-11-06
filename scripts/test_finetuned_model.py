"""
파인튜닝된 모델 간단 테스트 스크립트
10개의 테스트 프롬프트로 모델 성능을 평가합니다.
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from dotenv import load_dotenv

load_dotenv()


def load_finetuned_model(base_model_name: str, adapter_path: str):
    """파인튜닝된 모델 로드"""
    print("파인튜닝된 모델 로드 중...")

    # 양자화 설정 (4bit)
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
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
        base_model_name,
        trust_remote_code=True,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("모델 로드 완료!\n")
    return model, tokenizer


def generate_message(model, tokenizer, user_input: str) -> str:
    """메시지 생성"""
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
        # 첫 줄만 가져오기
        result = result.split('\n')[0].strip()
        return result
    else:
        return generated_text


def main():
    BASE_MODEL = os.getenv('MODEL_NAME', 'KORMo-Team/KORMo-10B-sft')
    ADAPTER_PATH = "./finetuned_model"

    if not os.path.exists(ADAPTER_PATH):
        print(f"파인튜닝된 모델이 없습니다: {ADAPTER_PATH}")
        print("먼저 finetune_model.py를 실행하세요.")
        return

    # 모델 로드
    model, tokenizer = load_finetuned_model(BASE_MODEL, ADAPTER_PATH)

    # 테스트 프롬프트 10개
    test_prompts = [
        "온도 37도 폭염주의보",
        "습도 88% 찜통더위",
        "기온 -5도 한파경보",
        "아침 8도 낮 26도 일교차",
        "변위계 이상 감지 안전점검",
        "강아지 산책 배변 처리",
        "미세먼지 매우나쁨 외출자제",
        "쓰레기 무단투기 금지",
        "겨울 눈길 미끄러움 주의",
        "온도 24도 습도 55% 화창함",
    ]

    print("=" * 80)
    print("파인튜닝 모델 테스트 (10개 프롬프트)")
    print("=" * 80)

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n[{i}/10]")
        print(f"입력: {prompt}")

        output = generate_message(model, tokenizer, prompt)

        print(f"출력: {output}")
        print(f"길이: {len(output)}자")
        print("-" * 80)

    print("\n평가 완료!")


if __name__ == "__main__":
    main()
