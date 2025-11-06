"""
DPO (Direct Preference Optimization) 파인튜닝 스크립트

목표:
- Chosen/Rejected 쌍으로 선호도 학습
- 규칙 없이 모델이 좋은 출력 패턴 학습
- Output cleaning 불필요
"""

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, PeftModel
from trl import DPOTrainer, DPOConfig
from dotenv import load_dotenv

load_dotenv()


def main():
    # 설정
    MODEL_NAME = os.getenv('MODEL_NAME', 'KORMo-Team/KORMo-10B-sft')
    BASE_MODEL_PATH = os.getenv('ADAPTER_PATH', './finetuned_model')  # 기존 파인튜닝 모델
    OUTPUT_DIR = "./finetuned_model_dpo"
    DPO_DATA_FILE = "data/dpo_dataset.jsonl"

    print(f"🚀 DPO 학습 시작")
    print(f"   베이스 모델: {MODEL_NAME}")
    print(f"   기존 어댑터: {BASE_MODEL_PATH}")
    print(f"   출력 경로: {OUTPUT_DIR}")

    # 1. 양자화 설정 (4bit)
    print("\n1️⃣ 양자화 설정 (4bit)...")
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    # 2. 토크나이저 로드
    print("\n2️⃣ 토크나이저 로드...")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
    )

    # 패딩 토큰 설정
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # 3. 베이스 모델 로드
    print("\n3️⃣ 베이스 모델 로드 (4bit 양자화)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )

    # 4. 기존 파인튜닝 어댑터 로드 (있다면)
    if os.path.exists(BASE_MODEL_PATH):
        print(f"\n4️⃣ 기존 어댑터 로드: {BASE_MODEL_PATH}")
        model = PeftModel.from_pretrained(model, BASE_MODEL_PATH)
        # DPO를 위해 merge & unload (선택적)
        # model = model.merge_and_unload()
        print("   ✓ 기존 어댑터 로드 완료")
    else:
        print(f"\n4️⃣ 기존 어댑터 없음, 베이스 모델로 진행")

    # 5. QLoRA 준비
    print("\n5️⃣ QLoRA 설정...")
    model = prepare_model_for_kbit_training(model)

    # LoRA 설정
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 6. DPO 데이터셋 로드
    print("\n6️⃣ DPO 데이터셋 로드...")
    dataset = load_dataset('json', data_files=DPO_DATA_FILE, split='train')

    print(f"   총 데이터: {len(dataset)}쌍")

    # 샘플 출력
    print("\n   [샘플]")
    sample = dataset[0]
    print(f"   프롬프트: {sample['prompt'][:60]}...")
    print(f"   Chosen: {sample['chosen'][:60]}...")
    print(f"   Rejected: {sample['rejected'][:60]}...")

    # 7. 학습 설정
    print("\n7️⃣ DPO 학습 설정...")
    training_args = DPOConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=5e-5,  # DPO는 낮은 학습률 사용
        fp16=True,
        logging_steps=5,
        save_strategy="steps",
        save_steps=50,
        save_total_limit=2,
        warmup_steps=10,
        lr_scheduler_type="cosine",
        optim="paged_adamw_8bit",
        report_to="none",
        gradient_checkpointing=True,
        remove_unused_columns=False,  # DPO에 중요
    )

    # 모델 설정
    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.use_cache = False

    # 8. DPO Trainer 설정
    print("\n8️⃣ DPO Trainer 설정...")

    # 최신 TRL API에 맞춰 단순화 (beta, max_length 등은 기본값 사용)
    dpo_trainer = DPOTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        processing_class=tokenizer,
    )

    # 9. 학습 시작
    print("\n9️⃣ DPO 학습 시작...\n")
    dpo_trainer.train()

    # 10. 모델 저장
    print("\n🔟 모델 저장...")
    dpo_trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"\n✅ DPO 학습 완료! 모델이 {OUTPUT_DIR}에 저장되었습니다.")

    # 11. 학습 통계 출력
    print("\n📊 학습 통계:")
    if dpo_trainer.state.log_history:
        losses = [x for x in dpo_trainer.state.log_history if 'loss' in x]

        if losses:
            initial_loss = losses[0].get('loss', 0)
            final_loss = losses[-1].get('loss', 0)
            print(f"  - 초기 손실: {initial_loss:.4f}")
            print(f"  - 최종 손실: {final_loss:.4f}")

            if initial_loss > 0:
                improvement = ((initial_loss - final_loss) / initial_loss * 100)
                print(f"  - 손실 개선: {improvement:.1f}%")

    print("\n🎯 효과:")
    print("  - 특수 토큰 자동 제거 학습")
    print("  - 질문 형식 자동 제거 학습")
    print("  - 간결하고 깔끔한 출력 학습")
    print("  - Output cleaning 규칙 불필요!")

    print("\n다음 단계:")
    print("  1. .env에서 ADAPTER_PATH를 ./finetuned_model_dpo로 변경")
    print("  2. 모델 서버 재시작")
    print("  3. 테스트 실행")


if __name__ == "__main__":
    main()


import requests

test_cases = [
  {"yesterday": 0, "today": 1, "expected": "1도 차이 - 특수토큰 없이 깔끔하게"},
  {"yesterday": -10, "today": 10, "expected": "20도 상승 - 질문 없이"},
  {"yesterday": 20, "today": 30, "expected": "10도 상승 - 간결하게"},
  {"yesterday": 30, "today": 20, "expected": "10도 하강 - 온도 차이 명시"},
]

for case in test_cases:
  prompt = f"어제의 평균온도는 {case['yesterday']}도고 오늘의 평균온도는 {case['today']}도야. " \
           f"이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘"

  response = requests.post(
      "http://localhost:8000/generate",
      json={"prompt": prompt, "max_new_tokens": 100}
  )

  result = response.json()
  print(f"\n{'='*60}")
  print(f"입력: {case['yesterday']}도 → {case['today']}도")
  print(f"기대: {case['expected']}")
  print(f"출력: {result['generated_text']}")
  print(f"{'='*60}")