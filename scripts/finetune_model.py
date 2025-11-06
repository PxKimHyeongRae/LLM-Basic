"""
QLoRA 파인튜닝 스크립트
KORMo-10B-sft 모델을 전광판 메시지 생성 태스크에 맞게 파인튜닝합니다.
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
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from dotenv import load_dotenv

load_dotenv()


def format_instruction(sample):
    """
    학습 데이터를 instruction 형식으로 포맷팅합니다.
    """
    instruction = f"""아래 입력을 공원 전광판에 표시할 메시지로 변환하세요.

입력: {sample['input']}
출력: {sample['output']}"""

    return instruction


def main():
    # 설정
    MODEL_NAME = os.getenv('MODEL_NAME', 'KORMo-Team/KORMo-10B-sft')
    OUTPUT_DIR = "./finetuned_model"
    TRAIN_FILE = "data/train_merged.jsonl"  # 기존 + 온도 비교 데이터 (401개)
    VAL_FILE = "data/validation.jsonl"

    print(f"🚀 파인튜닝 시작: {MODEL_NAME}")

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
        r=16,  # LoRA rank
        lora_alpha=32,  # LoRA alpha
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],  # KORMo의 attention 및 MLP 레이어
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

    # 데이터 포맷팅
    def formatting_func(example):
        text = f"""아래 입력을 공원 전광판에 표시할 메시지로 변환하세요.

입력: {example['input']}
출력: {example['output']}"""
        return text

    # 6. 학습 설정
    print("\n6️⃣ 학습 설정...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=1,  # 메모리 절약을 위해 1로 설정
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=8,  # 배치 크기를 줄인 만큼 증가
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        warmup_steps=50,
        lr_scheduler_type="cosine",
        optim="paged_adamw_8bit",
        report_to="none",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        gradient_checkpointing=True,  # 메모리 절약
    )

    # 모델의 토크나이저 설정
    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.use_cache = False  # gradient checkpointing과 충돌 방지

    # 7. Trainer 설정
    print("\n7️⃣ Trainer 설정...")

    # 데이터 전처리 함수
    def preprocess_function(examples):
        texts = []
        for inp, out in zip(examples['input'], examples['output']):
            text = f"""아래 입력을 공원 전광판에 표시할 메시지로 변환하세요.

입력: {inp}
출력: {out}"""
            texts.append(text)

        # 토크나이징
        model_inputs = tokenizer(
            texts,
            max_length=512,
            truncation=True,
            padding='max_length',
            return_tensors=None,
        )

        # labels 설정 (input_ids 복사)
        model_inputs["labels"] = model_inputs["input_ids"].copy()

        return model_inputs

    # 데이터셋 전처리
    train_dataset = train_dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=train_dataset.column_names,
    )

    val_dataset = val_dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=val_dataset.column_names,
    )

    from transformers import Trainer, DataCollatorForLanguageModeling

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )

    # 8. 학습 시작
    print("\n8️⃣ 학습 시작...\n")
    trainer.train()

    # 9. 모델 저장
    print("\n9️⃣ 모델 저장...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"\n✅ 파인튜닝 완료! 모델이 {OUTPUT_DIR}에 저장되었습니다.")

    # 10. 학습 통계 출력
    print("\n📊 학습 통계:")
    if trainer.state.log_history:
        train_losses = [x for x in trainer.state.log_history if 'loss' in x]
        eval_losses = [x for x in trainer.state.log_history if 'eval_loss' in x]

        if train_losses:
            final_train_loss = train_losses[-1]['loss']
            print(f"  - 최종 학습 손실: {final_train_loss:.4f}")

        if eval_losses:
            final_eval_loss = eval_losses[-1]['eval_loss']
            print(f"  - 최종 검증 손실: {final_eval_loss:.4f}")
        else:
            print(f"  - 검증 손실: 데이터가 적어 검증이 실행되지 않았습니다.")

        if train_losses:
            initial_loss = train_losses[0].get('loss', 0)
            final_loss = train_losses[-1].get('loss', 0)
            improvement = ((initial_loss - final_loss) / initial_loss * 100) if initial_loss > 0 else 0
            print(f"  - 손실 개선: {improvement:.1f}%")


if __name__ == "__main__":
    main()
