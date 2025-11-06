# Chat 형식 파인튜닝 빠른 시작 가이드

## 왜 Chat 형식인가?

현재 문제:
```
기대: "어제보다 10도 상승해 화창합니다. 가벼운 옷차림으로 나들이 즐기세요"
실제: "출력: 오늘은...", "---\n**메시지:**...", "(또는)..." 등 불필요한 레이블 포함
```

**해결책:** Chat 형식 파인튜닝
- ✅ 레이블 문제 완전 해결
- ✅ KORMo 모델 원래 학습 형식과 일치
- ✅ Inference 시 자연스러운 생성

---

## 실행 단계 (5분 안에 완료)

### 1️⃣ Chat 형식 데이터 생성 (30초)

```bash
python scripts/prepare_chat_format_data.py
```

**출력 확인:**
```
✅ 학습 데이터: 74개 → data/train_chat.jsonl
✅ 검증 데이터: 5개 → data/validation_chat.jsonl
```

### 2️⃣ 파인튜닝 스크립트 수정 (1분)

`scripts/finetune_model_temperature.py` 파일 열기:

**변경 전:**
```python
TRAIN_FILE = "data/train_temperature.jsonl"
VAL_FILE = "data/validation_temperature.jsonl"
OUTPUT_DIR = "./finetuned_model_temperature"
```

**변경 후:**
```python
TRAIN_FILE = "data/train_chat.jsonl"  # ← 이것만 변경
VAL_FILE = "data/validation_chat.jsonl"  # ← 이것만 변경
OUTPUT_DIR = "./finetuned_model_chat"  # ← 새 이름
```

### 3️⃣ 파인튜닝 실행 (30-60분)

```bash
python scripts/finetune_model_temperature.py
```

**진행 상황:**
```
Epoch 1/5: 100%|██████████| 74/74 [00:45<00:00,  1.64it/s]
Validation Loss: 0.234
...
✅ 파인튜닝 완료: ./finetuned_model_chat
```

### 4️⃣ .env 설정 (30초)

`.env` 파일 수정 (또는 생성):

```bash
# 파인튜닝 모델 사용
USE_FINETUNED=true
ADAPTER_PATH=./finetuned_model_chat

# Chat 형식 사용 (중요!)
USE_CHAT_FORMAT=true

# 양자화 설정
QUANTIZATION=4bit
```

### 5️⃣ 서버 시작 및 테스트 (1분)

**서버 시작:**
```bash
python model_server.py
```

**테스트:**
```bash
# PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/generate/temperature" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"yesterday_temp": 10, "today_temp": 20}'

# 또는 curl (Git Bash)
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{"yesterday_temp": 10, "today_temp": 20}'
```

**기대 결과:**
```json
{
  "generated_text": "어제보다 10도 상승해 화창합니다. 공원 나들이 즐기세요.",
  "prompt": "<|im_start|>system...",
  "generation_time": 2.1
}
```

---

## 파인튜닝 전 vs 후 비교

### Before (원본 모델 + Instruction 형식)

**입력:** 어제 10도, 오늘 20도

**출력:**
```
---
**전광판 메시지:**
오늘 공원은 따뜻합니다. 가벼운 옷차림으로 나오세요!

(또는)
어제보다 포근해졌습니다. 산책하기 좋은 날이에요.

---
두 문장 모두 자연스럽지만...
```

### After (Chat 형식 파인튜닝)

**입력:** 어제 10도, 오늘 20도

**출력:**
```
어제보다 10도 상승해 화창합니다. 공원 나들이 즐기세요.
```

✅ **개선 사항:**
1. 레이블 없음 (`출력:`, `---`, `**` 제거)
2. 온도 차이 명시 ("10도")
3. 간결한 한 문장
4. 공원 관련 조언 포함

---

## 다양한 케이스 테스트

```bash
# 큰 상승
{"yesterday_temp": 5, "today_temp": 20}
→ "어제보다 15도 상승해 포근합니다. 공원 산책 최고예요."

# 큰 하강
{"yesterday_temp": 35, "today_temp": 22}
→ "어제보다 13도 낮아져 시원해졌습니다. 공원 산책하기 좋아요."

# 온도 동일
{"yesterday_temp": 20, "today_temp": 20}
→ "어제와 비슷합니다. 공원에서 여유를 즐기세요."

# 극한 추위
{"yesterday_temp": -10, "today_temp": 0}
→ "어제보다 10도 올라 영상이 되었습니다. 공원 방문해보세요."

# 극한 더위
{"yesterday_temp": 30, "today_temp": 38}
→ "어제보다 8도 올라 매우 덥습니다. 실내 활동 권장합니다."
```

---

## 문제 해결

### ❌ 파인튜닝 후에도 "출력:"이 나와요

**원인:** Chat 형식을 사용하지 않음

**해결:**
```bash
# .env 확인
USE_CHAT_FORMAT=true  # ← 이것이 true인지 확인

# 서버 재시작
python model_server.py
```

### ❌ CUDA Out of Memory 에러

**해결:**
```bash
# .env에서 양자화 레벨 높이기
QUANTIZATION=4bit  # 8bit → 4bit 변경

# 또는 배치 사이즈 줄이기
# finetune_model_temperature.py에서:
per_device_train_batch_size=1  # 2 → 1
```

### ❌ 파인튜닝이 너무 느려요

**정상:** GPU 성능에 따라 30-60분 소요

**빠르게 하려면:**
```python
# finetune_model_temperature.py 수정
num_train_epochs=3  # 5 → 3 (빠르지만 품질 하락 가능)
```

### ❌ 생성된 메시지가 너무 짧거나 길어요

**해결:**
```python
# model_server.py의 GenerateRequest에서
max_new_tokens=50  # 기본값 조정 (40-70자 ≈ 20-35 토큰)
```

---

## 성능 개선 팁

### 1️⃣ 데이터 증강 (품질 향상)

`wrap_temperature_data.py`의 340개 데이터를 Chat 형식으로 변환:

```python
# prepare_chat_format_data.py에서 TRAIN_DATA 확장
from wrap_temperature_data import TRAIN_DATA as LARGE_DATA

# Chat 형식으로 변환 후 JSONL 저장
# → 340개 학습 데이터
```

### 2️⃣ 하이퍼파라미터 튜닝

```python
# finetune_model_temperature.py
num_train_epochs=10  # 더 오래 학습 (5 → 10)
learning_rate=2e-4   # 더 안정적 (3e-4 → 2e-4)
lora_r=64           # 더 많은 파라미터 (32 → 64)
```

### 3️⃣ Temperature 조정

```bash
# API 요청 시
{
  "yesterday_temp": 10,
  "today_temp": 20,
  "temperature": 0.5  # 낮을수록 일관적 (0.3-0.7 권장)
}
```

---

## 체크리스트

**파인튜닝 전:**
- [ ] `data/train_chat.jsonl` 생성 완료
- [ ] `data/validation_chat.jsonl` 생성 완료
- [ ] `finetune_model_temperature.py` 파일 경로 수정
- [ ] GPU 메모리 충분 (최소 6GB)

**파인튜닝 후:**
- [ ] `./finetuned_model_chat/` 폴더 생성됨
- [ ] `.env`에 `USE_FINETUNED=true` 설정
- [ ] `.env`에 `USE_CHAT_FORMAT=true` 설정
- [ ] `.env`에 `ADAPTER_PATH=./finetuned_model_chat` 설정

**테스트:**
- [ ] 서버 정상 시작 (http://localhost:8000)
- [ ] `/health` 엔드포인트 정상 응답
- [ ] `/generate/temperature` 정상 작동
- [ ] 레이블 없이 메시지만 생성됨
- [ ] 온도 차이 숫자로 명시됨
- [ ] 40-70자 길이 준수
- [ ] 공원 관련 조언 포함

---

## 다음 단계

### Phase 1: 기본 파인튜닝 ✅ (현재)
- Chat 형식 74개 데이터
- 기본 성능 확보

### Phase 2: 데이터 증강 (선택)
- 340개 데이터로 확장
- 다양한 케이스 커버

### Phase 3: DPO 최적화 (고급)
- 좋은 출력 vs 나쁜 출력 학습
- 완벽한 형식 제어

---

## 전체 명령어 요약

```bash
# 1. 데이터 생성
python scripts/prepare_chat_format_data.py

# 2. 파인튜닝 (finetune_model_temperature.py 수정 후)
python scripts/finetune_model_temperature.py

# 3. .env 설정
echo "USE_FINETUNED=true" >> .env
echo "ADAPTER_PATH=./finetuned_model_chat" >> .env
echo "USE_CHAT_FORMAT=true" >> .env

# 4. 서버 시작
python model_server.py

# 5. 테스트
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{"yesterday_temp": 10, "today_temp": 20}'
```

---

## 성공 지표

✅ **출력 형식:** 한 문장, 레이블 없음
✅ **정보 완전성:** 온도 차이 숫자로 명시
✅ **길이:** 40-70자
✅ **일관성:** 동일 입력에 유사한 출력
✅ **응답 시간:** 5초 이내

---

## 참고 문서

- 상세 비교: `FINETUNING_FORMAT_GUIDE.md`
- 전체 가이드: `CLAUDE.md`
- 프롬프트 템플릿: `src/generator/prompt_templates.py:181-203`
- 모델 서버: `model_server.py:362-404`

---

**마지막 업데이트:** 2025-11-06
**권장 방법:** Chat 형식 파인튜닝 (이 가이드)
