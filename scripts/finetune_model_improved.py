"""
개선된 파인튜닝 스크립트
온도 논리가 개선된 데이터로 재학습
"""

import os
import json
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from dotenv import load_dotenv

load_dotenv()


def main():
    # 설정
    MODEL_NAME = os.getenv('MODEL_NAME', 'KORMo-Team/KORMo-10B-sft')
    OUTPUT_DIR = "./finetuned_model_improved"

    # 개선된 데이터 사용
    TRAIN_FILE = "data/train_improved.jsonl"
    VAL_FILE = "data/validation_improved.jsonl"

    print("=" * 70)
    print(f"🚀 개선된 파인튜닝 시작: {MODEL_NAME}")
    print("   온도 논리가 개선된 데이터 사용")
    print(f"   학습 데이터: {TRAIN_FILE}")
    print("=" * 70)

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

    # 3. 모델 로드
    print("\n3️⃣ 모델 로드 (4bit 양자화)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )

    # 4. QLoRA를 위한 모델 준비
    print("\n4️⃣ QLoRA 설정...")
    model = prepare_model_for_kbit_training(model)

    # LoRA 설정
    lora_config = LoraConfig(
        r=32,
        lora_alpha=64,
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

    # 5. 데이터셋 로드
    print("\n5️⃣ 데이터셋 로드...")
    train_dataset = load_dataset('json', data_files=TRAIN_FILE, split='train')
    val_dataset = load_dataset('json', data_files=VAL_FILE, split='train')

    print(f"  - 학습 데이터: {len(train_dataset)}개")
    print(f"  - 검증 데이터: {len(val_dataset)}개")

    # 데이터 샘플 출력
    print("\n[학습 데이터 샘플]")
    print(train_dataset[0]['text'][:200] + "...")

    # 6. 데이터 전처리
    print("\n6️⃣ 데이터 전처리...")

    def preprocess_function(examples):
        model_inputs = tokenizer(
            examples['text'],
            max_length=512,
            truncation=True,
            padding='max_length',
            return_tensors=None,
        )
        model_inputs["labels"] = model_inputs["input_ids"].copy()
        return model_inputs

    train_dataset = train_dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=train_dataset.column_names,
        desc="학습 데이터 전처리"
    )

    val_dataset = val_dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=val_dataset.column_names,
        desc="검증 데이터 전처리"
    )

    # 7. 학습 설정
    print("\n7️⃣ 학습 설정...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=5,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=8,
        learning_rate=3e-4,
        fp16=True,
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=20,
        save_strategy="steps",
        save_steps=20,
        save_total_limit=3,
        warmup_steps=30,
        lr_scheduler_type="cosine",
        optim="paged_adamw_8bit",
        report_to="none",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        gradient_checkpointing=True,
        logging_first_step=True,
    )

    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.use_cache = False

    # 8. Data Collator
    print("\n8️⃣ Data Collator 설정...")
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    # 9. Trainer 설정
    print("\n9️⃣ Trainer 설정...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )

    # 10. 학습 시작
    print("\n" + "=" * 70)
    print("🔥 개선된 데이터로 학습 시작!")
    print("=" * 70 + "\n")

    trainer.train()

    # 11. 모델 저장
    print("\n" + "=" * 70)
    print("💾 모델 저장 중...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"✅ 파인튜닝 완료! 모델이 {OUTPUT_DIR}에 저장되었습니다.")

    # 12. 학습 통계 출력
    print("\n📊 학습 통계:")
    print("=" * 70)

    if trainer.state.log_history:
        train_losses = [x for x in trainer.state.log_history if 'loss' in x]
        eval_losses = [x for x in trainer.state.log_history if 'eval_loss' in x]

        if train_losses:
            initial_loss = train_losses[0].get('loss', 0)
            final_loss = train_losses[-1].get('loss', 0)
            print(f"  초기 학습 손실: {initial_loss:.4f}")
            print(f"  최종 학습 손실: {final_loss:.4f}")

            if initial_loss > 0:
                improvement = ((initial_loss - final_loss) / initial_loss * 100)
                print(f"  손실 개선율: {improvement:.1f}%")

        if eval_losses:
            best_eval_loss = min([x['eval_loss'] for x in eval_losses])
            print(f"  최고 검증 손실: {best_eval_loss:.4f}")

    print("\n" + "=" * 70)
    print("다음 단계:")
    print("  1. .env 파일에서 다음 설정 변경:")
    print(f"     USE_FINETUNED=true")
    print(f"     ADAPTER_PATH={OUTPUT_DIR}")
    print("  2. 모델 서버 재시작:")
    print("     python model_server.py")
    print("  3. 테스트:")
    print("     curl -X POST http://localhost:8000/generate/temperature \\")
    print("       -d '{\"yesterday_temp\": 35, \"today_temp\": 25}'")
    print("=" * 70)


if __name__ == "__main__":
    main()
