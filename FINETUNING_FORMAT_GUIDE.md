# 파인튜닝 데이터 형식 비교 가이드

## 문제 상황

현재 `wrap_temperature_data.py`로 파인튜닝했을 때:

**학습 데이터 형식:**
```
<instruction>
당신은 공원 전광판 메시지 전문가입니다...
</instruction>

<rules>
1. 반드시 한 문장만...
</rules>

<task>
입력: 어제 10도, 오늘 20도
출력: 어제보다 10도 상승해 화창합니다. 공원 나들이 즐기세요.
```

**문제점:**
1. 모델이 "출력:"이라는 레이블을 먼저 생성
2. Inference 시 프롬프트 형식과 불일치
3. 불필요하게 긴 instruction (매번 반복)

---

## 해결 방법 비교

### 방법 1: Instruction 간소화 (prepare_simple_training_data.py)

**장점:**
- 현재 프롬프트 구조 유지
- 빠른 적용 가능

**단점:**
- 여전히 레이블 문제 가능성
- Instruction 형식 비효율

**학습 데이터:**
```
<instruction>
공원 전광판 메시지를 한 문장으로 작성하세요.
- 마크다운, 특수문자, 이모지 사용 금지
- 온도 차이를 구체적 숫자로 명시
</instruction>

어제 10도, 오늘 20도
어제보다 10도 상승해 화창합니다. 공원 나들이 즐기세요.
```

---

### 방법 2: Chat 형식 ⭐ **추천**

**장점:**
- KORMo 모델의 원래 학습 형식과 일치
- 레이블 문제 완전 해결
- Inference 시 자연스러운 생성
- System/User/Assistant 역할 명확

**학습 데이터:**
```
<|im_start|>system
당신은 공원 전광판 메시지 전문가입니다. 온도 정보를 받아 40-70자 길이의 간결한 한 문장 메시지를 작성하세요.<|im_end|>
<|im_start|>user
어제 10도, 오늘 20도<|im_end|>
<|im_start|>assistant
어제보다 10도 상승해 화창합니다. 공원 나들이 즐기세요.<|im_end|>
```

**Inference 시:**
```python
prompt = """<|im_start|>system
당신은 공원 전광판 메시지 전문가입니다...<|im_end|>
<|im_start|>user
어제 15도, 오늘 25도<|im_end|>
<|im_start|>assistant
"""

# 모델이 여기서 자연스럽게 메시지 생성
# 레이블 없이 바로 메시지 출력
```

---

## 실행 방법

### Step 1: Chat 형식 데이터 생성

```bash
python scripts/prepare_chat_format_data.py
```

**출력:**
- `data/train_chat.jsonl` (74개)
- `data/validation_chat.jsonl` (5개)

### Step 2: 파인튜닝 스크립트 수정

`scripts/finetune_model_temperature.py` 파일에서:

```python
# 파일 경로 변경
TRAIN_FILE = "data/train_chat.jsonl"        # ← 변경
VAL_FILE = "data/validation_chat.jsonl"      # ← 변경
OUTPUT_DIR = "./finetuned_model_chat"        # ← 새 이름
```

### Step 3: 파인튜닝 실행

```bash
python scripts/finetune_model_temperature.py
```

예상 소요 시간: 30-60분 (GPU 성능에 따라)

### Step 4: model_server.py 수정

Chat 형식 사용하도록 엔드포인트 수정:

```python
@app.post("/generate/temperature", response_model=GenerateResponse)
async def generate_temperature_message(request: TemperatureComparisonRequest):
    if not model_loaded:
        raise HTTPException(status_code=503, detail="모델이 아직 로드 중입니다.")

    try:
        # Chat 형식 프롬프트 생성 (NEW!)
        structured_prompt = PromptTemplates.get_temperature_chat_prompt(
            request.yesterday_temp,
            request.today_temp
        )

        logger.info(f"온도 비교 메시지 생성: 어제 {request.yesterday_temp}도 → 오늘 {request.today_temp}도")

        gen_request = GenerateRequest(
            prompt=structured_prompt,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature
        )

        return await generate_text(gen_request)

    except Exception as e:
        logger.error(f"온도 비교 메시지 생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"생성 실패: {str(e)}")
```

### Step 5: .env 설정

```bash
USE_FINETUNED=true
ADAPTER_PATH=./finetuned_model_chat
```

### Step 6: 서버 재시작 및 테스트

```bash
# 서버 시작
python model_server.py

# 테스트
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{"yesterday_temp": 10, "today_temp": 20}'
```

**기대 결과:**
```json
{
  "generated_text": "어제보다 10도 상승해 화창합니다. 공원 나들이 즐기세요.",
  "prompt": "<|im_start|>system...",
  "generation_time": 2.3
}
```

---

## 형식별 비교표

| 특징 | wrap_temperature_data.py | prepare_simple_training_data.py | prepare_chat_format_data.py ⭐ |
|------|-------------------------|--------------------------------|------------------------------|
| **레이블 문제** | ❌ "출력:" 생성됨 | ⚠️ 여전히 가능성 있음 | ✅ 완전 해결 |
| **모델 호환성** | ⚠️ 일반 instruction 형식 | ⚠️ 일반 instruction 형식 | ✅ KORMo 원래 형식 |
| **프롬프트 길이** | ❌ 매우 김 (rules 포함) | ⚠️ 중간 | ✅ 간결 |
| **Inference 일치** | ❌ 불일치 | ⚠️ 부분 일치 | ✅ 완벽 일치 |
| **데이터 개수** | 340개 | 37개 | 74개 |
| **권장도** | ❌ 비추천 | ⚠️ 차선책 | ✅ 강력 추천 |

---

## 왜 Chat 형식이 최선인가?

### 1. KORMo 모델의 원래 학습 방식
KORMo-10B-sft는 **ChatML 형식**으로 학습됨:
```
<|im_start|>system
...<|im_end|>
<|im_start|>user
...<|im_end|>
<|im_start|>assistant
...<|im_end|>
```

### 2. 토큰 효율성
- Instruction 형식: 매번 긴 instruction 반복
- Chat 형식: System 프롬프트 한 번 + 짧은 User 메시지

### 3. 생성 품질
- Instruction: "출력:", "답:" 등 레이블 생성 가능성
- Chat: `<|im_start|>assistant` 다음에 바로 메시지 생성

### 4. 확장성
- 다양한 시스템 프롬프트로 쉽게 변경 가능
- Few-shot 예시 추가 용이

---

## 추가 최적화 방법

### 1. 데이터 증강 (더 많은 예시)

현재 74개 → 200-300개로 확장:

```python
# wrap_temperature_data.py의 TRAIN_DATA를 가져와서
# Chat 형식으로 변환
for yesterday, today, message in TRAIN_DATA:
    text = create_chat_format(yesterday, today, message)
    # JSONL에 저장
```

### 2. DPO (Direct Preference Optimization)

좋은 출력 vs 나쁜 출력 비교 학습:

```python
{
  "prompt": "<|im_start|>system...<|im_start|>user\n어제 10도, 오늘 20도<|im_end|>",
  "chosen": "어제보다 10도 상승해 화창합니다. 공원 나들이 즐기세요.",
  "rejected": "출력: 오늘은 더워졌습니다. (또는) 가벼운 옷차림..."
}
```

### 3. Stop Token 설정

Chat 형식에서는 `<|im_end|>` 토큰에서 자동 중단:

```python
outputs = model.generate(
    **inputs,
    max_new_tokens=50,
    eos_token_id=tokenizer.encode("<|im_end|>")[0],  # 자동 종료
    pad_token_id=tokenizer.eos_token_id
)
```

---

## 문제 해결

### Q1: Chat 형식으로 했는데도 레이블이 나와요

**A:** 토크나이저의 chat_template 확인:

```python
print(tokenizer.chat_template)
# None이 나오면 수동으로 ChatML 형식 사용 (위 방법 그대로)
```

### Q2: 생성 길이가 너무 짧거나 깁니다

**A:** max_new_tokens 조정:

```python
# 한국어 40-70자 ≈ 20-35 토큰
max_new_tokens=40  # 약간 여유있게
```

### Q3: 파인튜닝 후에도 품질이 안 좋아요

**A:** 다음 체크리스트:
1. ✅ 학습 데이터 품질 (메시지가 모두 좋은 예시인가?)
2. ✅ Epoch 수 (너무 적으면 underfit, 많으면 overfit)
3. ✅ Learning rate (3e-4가 보통 적절)
4. ✅ LoRA rank (32 또는 64)
5. ✅ 데이터 개수 (최소 50개 이상)

---

## 다음 단계

1. ✅ Chat 형식 데이터 생성: `python scripts/prepare_chat_format_data.py`
2. ⏳ 파인튜닝 실행 (30-60분)
3. ⏳ .env 설정 변경
4. ⏳ model_server.py 수정 (위 코드 참고)
5. ⏳ 서버 재시작 및 테스트

---

## 마지막 팁

**후처리 vs 파인튜닝:**
- ❌ 후처리 (if문, 정규식): AI 시범 사업 제약
- ✅ 파인튜닝: 순수 AI 방식, 근본적 해결

**Stop sequences vs EOS token:**
- Chat 형식에서는 `<|im_end|>` 자동 감지
- 별도 stopping_criteria 불필요

**성능 측정:**
```python
# 다양한 케이스로 테스트
test_cases = [
    (10, 20),   # 큰 상승
    (20, 10),   # 큰 하강
    (15, 15),   # 동일
    (-10, 5),   # 극한 상승
    (35, 25),   # 폭염 → 정상
]

for yesterday, today in test_cases:
    # API 호출 및 결과 확인
```
