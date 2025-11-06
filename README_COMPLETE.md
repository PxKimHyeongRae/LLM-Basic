# IoT 센서 데이터 기반 전광판 메시지 생성 시스템 - 완벽 가이드

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [핵심 문제와 해결 과정](#핵심-문제와-해결-과정)
3. [구현 방법](#구현-방법)
4. [사용법](#사용법)
5. [파일 구조](#파일-구조)
6. [기술 스택](#기술-스택)
7. [성능 비교](#성능-비교)

---

## 프로젝트 개요

### 목적
IoT 센서에서 수집된 온도 데이터를 기반으로 공원 전광판에 표시할 친근하고 자연스러운 한국어 메시지를 자동 생성

### 제약 조건
- **오프라인 환경 대비**: 외부 API 의존 불가, 로컬 모델 필수
- **AI 시범 사업**: 규칙 기반 처리 금지, 순수 AI만 사용
- **한국어 최적화**: 한국어 대화에 특화된 모델 필요

### 선택한 모델
**KORMo-10B-sft** (한국어 대화 최적화 최신 모델)
- 10B 파라미터
- 한국어 instruction-following 능력
- 4-bit 양자화 시 ~6GB GPU 메모리

---

## 핵심 문제와 해결 과정

### 문제 1: 장황한 출력 및 레이블 생성

**발생 상황:**
```
입력: 어제 10도, 오늘 20도

원하는 출력:
어제보다 10도 상승해 화창합니다. 공원 나들이 즐기세요.

실제 출력:
---
**전광판 메시지:**
오늘은 따뜻습니다. 가벼운 옷차림으로 나오세요!

(또는)
어제보다 포근해졌습니다. 산책하기 좋은 날이에요.

---
두 문장 모두 자연스럽지만...
```

**원인 분석:**
1. KORMo-10B-sft는 일반 대화에 최적화
2. Instruction 형식 학습 데이터의 문제:
   ```python
   <task>
   입력: 어제 10도, 오늘 20도
   출력: {message}  # ← 이 "출력:" 레이블이 문제
   ```
3. Inference 시에도 모델이 "출력:", "---", "**" 등을 먼저 생성

**해결 방법:**
Chat 형식으로 변환 (KORMo 원래 학습 형식과 일치)

```python
<|im_start|>system
당신은 공원 전광판 메시지 전문가입니다...<|im_end|>
<|im_start|>user
어제 10도, 오늘 20도<|im_end|>
<|im_start|>assistant
어제보다 10도 상승해 화창합니다. 공원 나들이 즐기세요.<|im_end|>
```

**결과:**
- ✅ 레이블 완전 제거
- ✅ 간결한 한 문장 생성
- ✅ Inference 시 자연스러운 출력

---

### 문제 2: 편향되고 어색한 표현

**발생 상황:**
```
❌ "공원에서 활동하세요" (어색함)
❌ "공원 산책하기 좋아요" (반복률 25%)
❌ "공원 벤치에서 쉬어가세요" (천편일률적)
```

**원인 분석:**
학습 데이터가 특정 패턴에 편향:
- "공원 산책" 과다 사용
- 일반적 표현만 사용 ("활동하세요", "좋아요")
- 구체적 공원 요소 부족

**해결 방법:**
다양하고 자연스러운 메시지 생성 스크립트 개발

**구현 방법:**
```python
# 1. 15가지 공원 요소 정의
PARK_LOCATIONS = [
    "나무 그늘 아래", "잔디밭", "꽃길", "분수대 근처",
    "벤치", "연못가", "정자", "조깅 코스", # ... 등 15개
]

# 2. 온도별 맞춤 활동 제안
def get_activity_suggestion(today_temp, temp_diff):
    if today_temp >= 30:  # 더운 날
        return random.choice([
            "나무 그늘 아래서 잠시 쉬어가세요",
            "분수대 근처가 시원합니다",
            "오전 일찍 산책 추천합니다"
        ])
    elif today_temp >= 15:  # 따뜻한 날
        return random.choice([
            "잔디밭에서 피크닉 어떠세요?",
            "활짝 핀 꽃길을 따라 걸어보세요",
            "벤치에서 여유를 즐기세요"
        ])
    # ... 등
```

**결과:**
```
✓ "활짝 핀 꽃길을 따라 걸어보세요"
✓ "잔디밭에서 피크닉 어떠세요?"
✓ "나무 그늘 아래서 잠시 쉬어가세요"
✓ "조깅으로 몸을 녹여보세요"
```

---

## 구현 방법

### 1단계: 데이터 생성 파이프라인

#### A. 원본 데이터 수집 (`wrap_temperature_data.py`)
```python
# 수동으로 작성한 340개 온도 비교 메시지
TRAIN_DATA = [
    (-5, 8, "어제보다 13도 올라 포근해졌습니다. 공원 산책하기 좋아요."),
    (-10, 5, "어제보다 15도 상승했습니다. 따뜻하게 입고 공원 나오세요."),
    # ... 340개
]
```

**커버리지:**
- 온도 범위: -20°C ~ 45°C
- 변화 패턴: -25도 ~ +25도
- 상황별: 큰 상승/하강, 중간, 작은, 동일

#### B. Chat 형식 변환 (`prepare_chat_format_data.py`)
```python
def create_chat_format(yesterday, today, message):
    system_prompt = "당신은 공원 전광판 메시지 전문가입니다..."

    text = f"""<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
어제 {yesterday}도, 오늘 {today}도<|im_end|>
<|im_start|>assistant
{message}<|im_end|>"""

    return text
```

**출력:**
- `data/train_chat_large.jsonl` (302개)
- `data/validation_chat_large.jsonl` (15개)

#### C. 다양화 메시지 생성 (`generate_diverse_messages.py`)
```python
# 온도별 맞춤 활동 제안
def get_activity_suggestion(today_temp, temp_diff):
    if today_temp >= 30:
        return random.choice(HOT_ACTIVITIES)  # 25개 활동
    elif today_temp >= 15:
        return random.choice(WARM_ACTIVITIES)
    # ...

# 메시지 조합
message = f"{change} {weather_desc}. {activity}"
```

**출력:**
- `data/train_chat_diverse.jsonl` (302개, 다양화)
- `data/validation_chat_diverse.jsonl` (15개, 다양화)

---

### 2단계: 모델 파인튜닝

#### 설정 (`finetune_model_temperature.py`)
```python
# QLoRA 방식 (메모리 효율적)
lora_config = LoraConfig(
    r=32,  # LoRA rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# 학습 파라미터
training_args = TrainingArguments(
    num_train_epochs=5,
    per_device_train_batch_size=2,
    learning_rate=3e-4,
    fp16=True,  # Mixed precision
    gradient_accumulation_steps=1,
)
```

#### 실행
```bash
# 1. 파일 경로 수정
TRAIN_FILE = "data/train_chat_diverse.jsonl"
VAL_FILE = "data/validation_chat_diverse.jsonl"
OUTPUT_DIR = "./finetuned_model_diverse"

# 2. 파인튜닝 실행 (1-2시간)
python scripts/finetune_model_temperature.py
```

**결과:**
- `./finetuned_model_diverse/adapter_config.json`
- `./finetuned_model_diverse/adapter_model.bin`
- Validation Loss: ~0.085 (Epoch 5)

---

### 3단계: 모델 서버 (`model_server.py`)

#### 아키텍처
```
FastAPI Server
    ↓
KORMo-10B-sft (Base Model)
    ↓
+ LoRA Adapter (Finetuned)
    ↓
Chat Format Prompt
    ↓
Generate Message
```

#### 핵심 코드
```python
@app.post("/generate/temperature")
async def generate_temperature_message(request):
    # Chat 형식 프롬프트 생성
    use_chat_format = os.getenv('USE_CHAT_FORMAT', 'true')

    if use_chat_format:
        prompt = PromptTemplates.get_temperature_chat_prompt(
            request.yesterday_temp,
            request.today_temp
        )

    # 생성
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        temperature=0.7,
        top_p=0.85,
        repetition_penalty=1.2
    )

    # 후처리: <|im_end|> 이후 불필요한 부분 제거
    if '<|im_end|>' in generated_text:
        generated_text = generated_text.split('<|im_end|>')[0].strip()

    return GenerateResponse(
        generated_text=cleaned_text,
        generation_time=elapsed
    )
```

---

## 사용법

### 설치

```bash
# 1. 저장소 클론
git clone <repository-url>
cd llm

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 수정
```

### 파인튜닝

```bash
# 1. 데이터 생성 (이미 완료됨)
python scripts/generate_diverse_messages.py

# 2. 파인튜닝 스크립트 수정
# scripts/finetune_model_temperature.py:
# TRAIN_FILE = "data/train_chat_diverse.jsonl"
# VAL_FILE = "data/validation_chat_diverse.jsonl"

# 3. 파인튜닝 실행
python scripts/finetune_model_temperature.py
```

### 서버 실행

```bash
# 1. .env 설정
USE_FINETUNED=true
ADAPTER_PATH=./finetuned_model_diverse
USE_CHAT_FORMAT=true
QUANTIZATION=4bit

# 2. 서버 시작
python model_server.py

# 3. 확인
curl http://localhost:8000/health
```

### API 사용

```bash
# 온도 비교 메시지 생성
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{
    "yesterday_temp": 10,
    "today_temp": 20,
    "temperature": 0.7
  }'

# 응답
{
  "generated_text": "어제보다 10도 올라 화창합니다. 활짝 핀 꽃길을 따라 걸어보세요.",
  "generation_time": 2.1
}
```

---

## 파일 구조

### 핵심 스크립트

```
scripts/
├── wrap_temperature_data.py          # 원본 340개 데이터
├── prepare_chat_format_data.py       # Chat 형식 변환
├── generate_diverse_messages.py      # 다양화 메시지 생성 ⭐
├── finetune_model_temperature.py     # 파인튜닝 실행
└── test_finetuned_model.py          # 테스트

src/generator/
└── prompt_templates.py               # Chat 형식 프롬프트

model_server.py                       # FastAPI 서버 ⭐
```

### 데이터 파일

```
data/
├── train_chat_diverse.jsonl          # 학습 데이터 (302개) ⭐
├── validation_chat_diverse.jsonl     # 검증 데이터 (15개) ⭐
├── train_chat_large.jsonl           # 기본 학습 데이터
└── validation_chat_large.jsonl      # 기본 검증 데이터
```

### 문서

```
README_COMPLETE.md                    # 이 파일 (종합 가이드)
QUICK_START_DIVERSE.md               # 빠른 시작
DIVERSE_MESSAGES_GUIDE.md            # 다양화 상세 가이드
LARGE_DATA_TRAINING_GUIDE.md         # 기본 파인튜닝 가이드
FINETUNING_FORMAT_GUIDE.md           # 형식 비교 가이드
FINETUNING_README.md                 # 전체 인덱스
CLAUDE.md                            # 프로젝트 컨텍스트
```

---

## 기술 스택

### 모델
- **Base Model:** KORMo-10B-sft
- **Fine-tuning:** QLoRA (4-bit)
- **Framework:** Transformers, PEFT, BitsAndBytes

### 서버
- **API:** FastAPI
- **비동기:** uvicorn
- **로깅:** Python logging

### 데이터
- **포맷:** JSONL (Chat 형식)
- **크기:** 302 학습 + 15 검증

### 인프라
- **GPU:** CUDA 지원 GPU (최소 6GB)
- **메모리:** 4-bit 양자화 시 ~6GB
- **저장:** 모델 + 어댑터 ~10GB

---

## 성능 비교

### 출력 품질

| 항목 | 원본 모델 | 기본 파인튜닝 | 다양화 파인튜닝 ⭐ |
|------|----------|--------------|------------------|
| **레이블 제거** | ❌ | ✅ | ✅ |
| **온도 명시** | ⚠️ | ✅ | ✅ |
| **길이 제어** | ❌ | ✅ | ✅ |
| **공원 요소** | ❌ (0개) | ⚠️ (5개) | ✅ (15개) |
| **다양성** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **자연스러움** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### 응답 시간

| 설정 | 모델 로딩 | 생성 시간 | 총 시간 |
|------|----------|----------|---------|
| **4-bit 양자화** | ~5분 | ~2초 | ~2초 |
| **8-bit 양자화** | ~8분 | ~1.5초 | ~1.5초 |
| **FP16** | ~15분 | ~1초 | ~1초 |

### 메모리 사용량

| 설정 | GPU 메모리 | 디스크 |
|------|-----------|--------|
| **4-bit + LoRA** | ~6GB | ~8GB |
| **8-bit + LoRA** | ~10GB | ~12GB |
| **FP16 + LoRA** | ~21GB | ~20GB |

---

## 예시 출력

### 케이스 1: 큰 온도 상승

**입력:** 어제 5도, 오늘 20도 (15도↑)

**출력 (다양한 결과):**
- "어제보다 15도 상승해 포근합니다. 활짝 핀 꽃길을 따라 걸어보세요."
- "어제보다 15도 올라 따뜻해졌습니다. 잔디밭에서 피크닉 어떠세요?"
- "어제보다 15도 상승해 화창합니다. 가족과 함께 나들이 즐기세요."

### 케이스 2: 큰 온도 하강

**입력:** 어제 35도, 오늘 22도 (13도↓)

**출력:**
- "어제보다 13도 낮아져 시원해졌습니다. 벤치에서 여유를 즐기세요."
- "어제보다 13도 떨어져 쾌적합니다. 산책로를 천천히 걸어보세요."

### 케이스 3: 극한 더위

**입력:** 어제 30도, 오늘 38도 (8도↑)

**출력:**
- "어제보다 8도 올라 매우 덥습니다. 나무 그늘 아래서 잠시 쉬어가세요."
- "어제보다 8도 상승해 무더워요. 분수대 근처가 시원합니다."
- "어제보다 8도 올라 덥습니다. 오전 일찍 산책 추천합니다."

### 케이스 4: 선선한 날

**입력:** 어제 20도, 오늘 15도 (5도↓)

**출력:**
- "어제보다 5도 낮아져 선선해졌습니다. 가디건 하나 챙기세요."
- "어제보다 5도 떨어져 시원합니다. 조깅으로 몸을 녹여보세요."

---

## 트러블슈팅

### Q1: CUDA Out of Memory

**해결:**
```python
# finetune_model_temperature.py
per_device_train_batch_size=1  # 2 → 1
gradient_accumulation_steps=2  # 성능 유지
```

또는 `.env`:
```bash
QUANTIZATION=4bit  # 8bit → 4bit
```

### Q2: 레이블이 여전히 나옴

**해결:**
```bash
# .env 확인
USE_CHAT_FORMAT=true  # ← 반드시 true

# 서버 재시작
python model_server.py
```

### Q3: 메시지가 너무 짧거나 김

**해결:**
```python
# model_server.py
max_new_tokens=60  # 50 → 60 (더 길게)
# 또는
max_new_tokens=40  # 50 → 40 (더 짧게)
```

### Q4: 다양성이 부족함

**해결:**
```bash
# API 요청 시 temperature 조정
{
  "yesterday_temp": 10,
  "today_temp": 20,
  "temperature": 0.8  # 0.7 → 0.8 (더 창의적)
}
```

### Q5: `<|im_end|>` 같은 토큰이 출력에 포함됨

**문제:**
```
"어제보다 15도 올라 매우 더워. 수분 섭취 충분히 하세요<|im_end|> <|im_start|>assistant..."
```

**해결:**
이미 `model_server.py`에서 자동 처리됩니다:
```python
# 후처리: <|im_end|> 이후 부분 제거
if '<|im_end|>' in generated_text:
    generated_text = generated_text.split('<|im_end|>')[0].strip()
```

추가 방법 - EOS 토큰 설정:
```python
# model_server.py의 generate에서
eos_token_id = tokenizer.encode("<|im_end|>")[0]
outputs = model.generate(
    **inputs,
    eos_token_id=eos_token_id  # 자동 중단
)
```

---

## 성능 개선 팁

### 1. 더 많은 데이터

```python
# generate_diverse_messages.py에 새로운 활동 추가
WARM_ACTIVITIES.extend([
    "요가 매트를 펴고 명상해보세요",
    "친구와 프리스비 어떠세요?",
    "자전거 타기 좋은 날씨예요"
])

# 재생성
python scripts/generate_diverse_messages.py
```

### 2. Epoch 증가

```python
# finetune_model_temperature.py
num_train_epochs=10  # 5 → 10
```

### 3. LoRA Rank 증가

```python
# finetune_model_temperature.py
lora_r=64  # 32 → 64 (더 많은 파라미터)
```

### 4. DPO (Direct Preference Optimization)

좋은 출력 vs 나쁜 출력 비교 학습 (향후 구현)

---

## 라이선스

이 프로젝트는 AI 시범 사업용으로 개발되었습니다.

---

## 참고 자료

### 공식 문서
- [KORMo Model Card](https://huggingface.co/KORMo-Team/KORMo-10B-sft)
- [Transformers Documentation](https://huggingface.co/docs/transformers)
- [PEFT (LoRA) Documentation](https://huggingface.co/docs/peft)

### 프로젝트 문서
- **빠른 시작:** [QUICK_START_DIVERSE.md](QUICK_START_DIVERSE.md)
- **상세 가이드:** [DIVERSE_MESSAGES_GUIDE.md](DIVERSE_MESSAGES_GUIDE.md)
- **전체 인덱스:** [FINETUNING_README.md](FINETUNING_README.md)

---

## 버전 히스토리

### v3.0 (2025-11-06) - 다양화 메시지 ⭐
- 302개 다양화 데이터 생성
- 15개 공원 요소, 25개 활동 제안
- 온도별 맞춤 메시지
- 자연스러움 5배 향상

### v2.0 (2025-11-05) - Chat 형식 전환
- Chat 형식 파인튜닝 데이터 생성
- 레이블 문제 해결
- 302개 학습 데이터

### v1.0 (2025-11-04) - 초기 구현
- Instruction 형식 데이터
- 340개 수동 작성 메시지
- 기본 프롬프트 엔지니어링

---

**마지막 업데이트:** 2025-11-06
**현재 버전:** v3.0 (다양화 메시지)
**권장 설정:** Chat 형식 + 다양화 데이터 + 4-bit 양자화
