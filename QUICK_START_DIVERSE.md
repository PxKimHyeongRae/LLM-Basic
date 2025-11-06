# 최신! 자연스러운 메시지 파인튜닝 빠른 시작

## 🎯 목표

**기존 문제:**
```
❌ "공원에서 활동하세요" (어색함)
❌ "공원 산책하기 좋아요" (반복적)
```

**해결:**
```
✓ "활짝 핀 꽃길을 따라 걸어보세요"
✓ "잔디밭에서 피크닉 어떠세요?"
✓ "나무 그늘 아래서 잠시 쉬어가세요"
```

---

## ✅ 데이터 준비 완료!

```
✓ data/train_chat_diverse.jsonl (302개)
✓ data/validation_chat_diverse.jsonl (15개)
```

**특징:**
- 15가지 공원 요소 (나무 그늘, 잔디밭, 꽃길, 분수대 등)
- 25가지 활동 제안 (피크닉, 조깅, 산책, 사진 촬영 등)
- 온도별 맞춤 메시지
- 다양한 문장 어미

---

## 🚀 3단계 실행

### 1️⃣ 파인튜닝 스크립트 수정 (1분)

`scripts/finetune_model_temperature.py`:

```python
TRAIN_FILE = "data/train_chat_diverse.jsonl"
VAL_FILE = "data/validation_chat_diverse.jsonl"
OUTPUT_DIR = "./finetuned_model_diverse"
```

### 2️⃣ 파인튜닝 실행 (1-2시간)

```bash
python scripts/finetune_model_temperature.py
```

### 3️⃣ 서버 설정 및 시작 (1분)

`.env`:
```bash
USE_FINETUNED=true
ADAPTER_PATH=./finetuned_model_diverse
USE_CHAT_FORMAT=true
```

서버 시작:
```bash
python model_server.py
```

---

## 🎨 결과 예시

### 테스트 1: 따뜻한 날

```bash
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{"yesterday_temp": 10, "today_temp": 23}'
```

**가능한 출력:**
- "어제보다 13도 올라 화창합니다. 활짝 핀 꽃길을 따라 걸어보세요."
- "어제보다 13도 상승해 따뜻해졌습니다. 잔디밭에서 피크닉 어떠세요?"
- "어제보다 13도 올라 포근합니다. 산책로를 천천히 걸어보세요."

### 테스트 2: 더운 날

```bash
curl -X POST "http://localhost:8000/generate/temperature" \
  -d '{"yesterday_temp": 25, "today_temp": 35}'
```

**가능한 출력:**
- "어제보다 10도 올라 매우 덥습니다. 나무 그늘 아래서 잠시 쉬어가세요."
- "어제보다 10도 상승해 무더워요. 분수대 근처가 시원합니다."
- "어제보다 10도 올라 덥습니다. 오전 일찍 산책 추천합니다."

### 테스트 3: 선선한 날

```bash
curl -X POST "http://localhost:8000/generate/temperature" \
  -d '{"yesterday_temp": 20, "today_temp": 15}'
```

**가능한 출력:**
- "어제보다 5도 낮아져 선선해졌습니다. 가디건 하나 챙기세요."
- "어제보다 5도 떨어져 시원합니다. 산책하며 단풍을 감상하세요."
- "어제보다 5도 낮아져 선선합니다. 조깅으로 몸을 녹여보세요."

---

## 📊 비교

| 항목 | 기존 (large) | 새 버전 (diverse) ⭐ |
|------|--------------|---------------------|
| **데이터 개수** | 302개 | 302개 |
| **공원 요소** | 5개 | **15개** ✨ |
| **활동 제안** | 8개 | **25개** ✨ |
| **자연스러움** | ⭐⭐⭐ | **⭐⭐⭐⭐⭐** ✨ |
| **다양성** | ⭐⭐⭐ | **⭐⭐⭐⭐⭐** ✨ |

---

## 📝 전체 명령어

```bash
# 1. 데이터 이미 생성됨!
# data/train_chat_diverse.jsonl (302개)
# data/validation_chat_diverse.jsonl (15개)

# 2. finetune_model_temperature.py 수정
# TRAIN_FILE = "data/train_chat_diverse.jsonl"
# VAL_FILE = "data/validation_chat_diverse.jsonl"
# OUTPUT_DIR = "./finetuned_model_diverse"

# 3. 파인튜닝 실행
python scripts/finetune_model_temperature.py

# 4. .env 설정
# USE_FINETUNED=true
# ADAPTER_PATH=./finetuned_model_diverse
# USE_CHAT_FORMAT=true

# 5. 서버 시작
python model_server.py

# 6. 테스트
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{"yesterday_temp": 10, "today_temp": 20}'
```

---

## 🎉 성공 지표

✅ 다양한 공원 요소 언급 (나무 그늘, 잔디밭, 꽃길 등)
✅ 온도별 적절한 활동 제안
✅ 자연스러운 문장 어미 (~어떠세요?, ~해보세요)
✅ 40-70자 길이 준수
✅ 레이블 없이 메시지만 생성
✅ 온도 차이 숫자로 명시

---

## 📚 더 자세한 정보

- **상세 가이드:** [DIVERSE_MESSAGES_GUIDE.md](DIVERSE_MESSAGES_GUIDE.md)
- **전체 인덱스:** [FINETUNING_README.md](FINETUNING_README.md)
- **형식 비교:** [FINETUNING_FORMAT_GUIDE.md](FINETUNING_FORMAT_GUIDE.md)

---

**마지막 업데이트:** 2025-11-06
**버전:** Diverse (최신)
**데이터:** 302개 다양화 메시지
**품질:** ⭐⭐⭐⭐⭐
