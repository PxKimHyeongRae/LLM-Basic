# Phase 0: 규칙 기반 제거 및 LLM 중심 파이프라인

## 🎯 핵심 개념

**"규칙을 짜지 말고, 모델이 학습하게 하자"**

- ❌ Before: 100줄 if/else, 50줄 regex 규칙
- ✅ After: Claude 생성 + DPO 학습 = 규칙 없음

---

## 📦 전체 흐름

```
┌─────────────────┐
│  로컬 (Windows) │
└─────────────────┘
  1. Claude API로 500개 데이터 생성
  2. DPO 데이터셋 생성 (16-20쌍)
  3. 파일 저장
          ↓
     파일 전송
          ↓
┌─────────────────┐
│   서버 (Linux)  │
└─────────────────┘
  4. DPO 학습 실행
  5. 모델 배포
  6. 테스트
```

---

## 🚀 로컬 실행 (Windows)

### 1. Anthropic API 키 설정

```bash
# .env 파일 수정
notepad .env

# 다음 줄 추가:
ANTHROPIC_API_KEY=sk-ant-여기에_발급받은_키
```

API 키 발급: https://console.anthropic.com/

### 2. Python 패키지 설치

```bash
pip install anthropic
```

### 3. Claude로 500개 데이터 생성 (5-10분)

```bash
python scripts\generate_with_claude.py
```

**결과**: `data\training_data_claude.jsonl` (약 500개)

### 4. DPO 데이터셋 생성 (2-3분)

```bash
python scripts\generate_dpo_dataset.py
```

**결과**: `data\dpo_dataset.jsonl` (약 16-20쌍)

### 5. 생성된 파일 확인

```bash
# PowerShell
Get-Content data\training_data_claude.jsonl | Measure-Object -Line
Get-Content data\dpo_dataset.jsonl | Measure-Object -Line
```

---

## 📤 서버로 파일 전송

### 방법 1: SCP (권장)

```bash
scp data\training_data_claude.jsonl pluxity@서버IP:~/lay/llm/data/
scp data\dpo_dataset.jsonl pluxity@서버IP:~/lay/llm/data/
```

### 방법 2: WinSCP (GUI)

1. WinSCP 실행
2. 서버 접속
3. 파일 드래그 앤 드롭

---

## 🎓 서버에서 학습 (Linux)

### 1. 파일 확인

```bash
cd ~/lay/llm
ls -lh data/training_data_claude.jsonl
ls -lh data/dpo_dataset.jsonl
```

### 2. 일반 파인튜닝 (선택사항)

Claude 생성 데이터로 먼저 일반 파인튜닝:

```bash
# scripts/finetune_model.py 수정
# TRAIN_FILE = "data/training_data_claude.jsonl" 로 변경

conda activate ml
python scripts/finetune_model.py
```

**예상 시간**: 5-10분

### 3. DPO 학습 (핵심!)

```bash
python scripts/finetune_dpo.py
```

**예상 시간**: 10-15분

**결과**: `finetuned_model_dpo/` 생성

### 4. 모델 적용

```bash
# .env 수정
nano .env

# ADAPTER_PATH를 변경:
ADAPTER_PATH=./finetuned_model_dpo
```

### 5. 모델 서버 재시작

```bash
pkill -f model_server.py
python model_server.py
```

---

## ✅ 테스트

### 테스트 프롬프트:

```python
# 서버에서 실행
from transformers import AutoTokenizer
from peft import PeftModel, AutoModelForCausalLM
import torch

# 모델 로드
model = AutoModelForCausalLM.from_pretrained(
    "KORMo-Team/KORMo-10B-sft",
    device_map="auto",
    torch_dtype=torch.float16
)
model = PeftModel.from_pretrained(model, "./finetuned_model_dpo")
tokenizer = AutoTokenizer.from_pretrained("KORMo-Team/KORMo-10B-sft")

# 테스트
test_prompt = """아래 입력을 공원 전광판에 표시할 메시지로 변환하세요.

입력: 어제 0도, 오늘 1도
출력:"""

inputs = tokenizer(test_prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=100)
result = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(result)
```

### 예상 결과:

**Before (규칙 기반):**
```
.<think>...</think>
전광판에 표시할 메시지:

안녕하세요, 오늘 공원은 더 시원합니다...

이 메시지가 적절한가요?
```

**After (DPO 학습):**
```
어제보다 1도 따뜻해졌습니다. 산책하기 좋은 날씨예요.
```

---

## 📊 효과

### Before (Phase 0 이전):
- ❌ `generate_comparison_data.py`: 100줄 if/else
- ❌ `output_cleaner.py`: 50줄 regex
- ❌ 315개 규칙 생성 데이터
- ❌ 새 상황 대응 불가

### After (Phase 0):
- ✅ Claude 생성: 500개, 규칙 없음
- ✅ DPO 학습: 자동으로 깔끔한 출력
- ✅ 후처리 불필요
- ✅ 확장 용이

---

## 🗂️ 파일 정리

### 더 이상 사용 안 함 (archive로 이동):
- `scripts/generate_comparison_data.py`
- `scripts/generate_training_data_manual.py`
- `scripts/fix_comparison_data.py`
- `src/generator/output_cleaner.py`
- `data/train_merged.jsonl`

### 새로 사용:
- ✅ `scripts/generate_with_claude.py`
- ✅ `scripts/generate_dpo_dataset.py`
- ✅ `scripts/finetune_dpo.py`
- ✅ `data/training_data_claude.jsonl`
- ✅ `data/dpo_dataset.jsonl`

---

## 🆘 문제 해결

### "ANTHROPIC_API_KEY not found"
→ .env 파일에 API 키 추가

### "Module 'anthropic' not found"
→ `pip install anthropic` 실행

### DPO 학습 시 CUDA OOM
→ `scripts/finetune_dpo.py`에서 `gradient_accumulation_steps`를 8로 증가

### 파일 전송 실패
→ WinSCP 또는 파일 내용 복사/붙여넣기 사용

---

## 💡 다음 단계

1. ✅ 로컬에서 데이터 생성
2. ✅ 서버로 파일 전송
3. ✅ DPO 학습 실행
4. ⏳ 모델 테스트
5. ⏳ Claude 평가 루프 구축
6. ⏳ 반복 개선

---

## 📞 완료 후

모든 단계가 끝나면 "완료했어"라고 알려주세요!
테스트 결과를 공유해주시면 추가 개선 방향을 제시하겠습니다.
