# 파인튜닝 완벽 가이드 인덱스

## 🚀 빠른 시작

지금 바로 시작하고 싶다면:
👉 **[DIVERSE_MESSAGES_GUIDE.md](DIVERSE_MESSAGES_GUIDE.md)** ⭐⭐ 최신! 가장 추천!
👉 **[LARGE_DATA_TRAINING_GUIDE.md](LARGE_DATA_TRAINING_GUIDE.md)** ⭐ 기본 버전

---

## 📚 문서 구조

### 1. 빠른 실행 가이드
- **[DIVERSE_MESSAGES_GUIDE.md](DIVERSE_MESSAGES_GUIDE.md)** ⭐⭐ **최신!**
  - **302개 다양화 데이터** Chat 형식 파인튜닝
  - 자연스럽고 구체적인 표현 (나무 그늘, 잔디밭, 꽃길 등)
  - 온도별 맞춤 활동 제안
  - **가장 추천!**

- **[LARGE_DATA_TRAINING_GUIDE.md](LARGE_DATA_TRAINING_GUIDE.md)** ⭐
  - 302개 기본 데이터
  - 기본 Chat 형식
  - 안정적인 성능

### 2. 상세 비교 문서
- **[FINETUNING_FORMAT_GUIDE.md](FINETUNING_FORMAT_GUIDE.md)**
  - 3가지 데이터 형식 비교
  - Instruction vs Chat 형식 차이
  - 왜 Chat 형식이 최선인가?
  - 문제 해결 가이드

### 3. 프로젝트 전체 컨텍스트
- **[CLAUDE.md](CLAUDE.md)**
  - 프로젝트 개요 및 현재 상황
  - 완료된 작업 목록
  - 기술적 제약사항
  - 전체 로드맵

---

## 🎯 상황별 가이드 선택

### "지금 바로 파인튜닝 하고 싶어요!"
👉 [LARGE_DATA_TRAINING_GUIDE.md](LARGE_DATA_TRAINING_GUIDE.md)
- 데이터 이미 준비됨 (302개)
- 3단계만 따라하면 완료

### "왜 Chat 형식을 사용해야 하나요?"
👉 [FINETUNING_FORMAT_GUIDE.md](FINETUNING_FORMAT_GUIDE.md)
- 형식별 장단점 비교
- 레이블 문제 해결 원리
- KORMo 모델 특성

### "프로젝트 전체를 이해하고 싶어요"
👉 [CLAUDE.md](CLAUDE.md)
- 시작부터 현재까지의 과정
- 시도한 방법들과 결과
- 앞으로의 계획

---

## 📊 데이터 현황

### 생성된 데이터 파일

| 파일명 | 개수 | 형식 | 품질 | 용도 |
|--------|------|------|------|------|
| `data/train_chat_diverse.jsonl` | 302개 | Chat | 다양화 ⭐⭐ | 학습 (최신!) |
| `data/validation_chat_diverse.jsonl` | 15개 | Chat | 다양화 ⭐⭐ | 검증 (최신!) |
| `data/train_chat_large.jsonl` | 302개 | Chat | 기본 ⭐ | 학습 |
| `data/validation_chat_large.jsonl` | 15개 | Chat | 기본 ⭐ | 검증 |
| `data/train_temperature.jsonl` | 340개 | Instruction | 레거시 | 레거시 |

**가장 추천:** `train_chat_diverse.jsonl` + `validation_chat_diverse.jsonl` (302+15개) ⭐⭐

---

## 🔧 핵심 스크립트

### 데이터 생성
```bash
# Chat 형식 대량 데이터 (302개) - 추천!
python scripts/prepare_chat_format_data.py
```

### 파인튜닝 실행
```bash
# 1. scripts/finetune_model_temperature.py 수정
# TRAIN_FILE = "data/train_chat_large.jsonl"
# VAL_FILE = "data/validation_chat_large.jsonl"
# OUTPUT_DIR = "./finetuned_model_chat_large"

# 2. 실행
python scripts/finetune_model_temperature.py
```

### 서버 시작
```bash
# 1. .env 설정
# USE_FINETUNED=true
# ADAPTER_PATH=./finetuned_model_chat_large
# USE_CHAT_FORMAT=true

# 2. 서버 시작
python model_server.py
```

---

## 📈 기대 효과

### Before (원본 모델)
```
입력: 어제 10도, 오늘 20도

출력:
---
**전광판 메시지:**
오늘은 따뜻합니다. 가벼운 옷차림으로...

(또는)
어제보다 포근해졌습니다...
```

❌ 문제점:
- 레이블 포함 (`출력:`, `---`, `**`)
- 온도 차이 명시 안 됨
- 너무 장황함

### After (Chat 형식 302개 다양화 파인튜닝) ⭐⭐
```
입력: 어제 10도, 오늘 20도

출력 (다양한 결과):
- "어제보다 10도 올라 화창합니다. 활짝 핀 꽃길을 따라 걸어보세요."
- "어제보다 10도 상승해 따뜻해졌습니다. 잔디밭에서 피크닉 어떠세요?"
- "어제보다 10도 올라 포근합니다. 벤치에서 여유를 즐기세요."
```

✅ 개선사항:
- ✨ **자연스럽고 다양한 표현** (NEW!)
- ✨ **구체적인 공원 요소 명시** (꽃길, 잔디밭 등) (NEW!)
- ✅ 레이블 없음
- ✅ 온도 차이 명시 ("10도")
- ✅ 간결한 한 문장
- ✅ 공원 관련 조언 포함

---

## 🎓 학습 곡선

### Level 1: 기본 이해
1. [LARGE_DATA_TRAINING_GUIDE.md](LARGE_DATA_TRAINING_GUIDE.md) 처음부터 끝까지 읽기
2. 3단계 따라하기
3. 테스트 케이스로 결과 확인

**소요 시간:** 2-3시간 (학습 1-2시간 + 실행 1시간)

### Level 2: 심화 학습
1. [FINETUNING_FORMAT_GUIDE.md](FINETUNING_FORMAT_GUIDE.md)로 원리 이해
2. 하이퍼파라미터 조정 실험
3. 다양한 temperature 값 테스트

**소요 시간:** 1-2일

### Level 3: 고급 최적화
1. DPO 적용
2. LoRA rank 조정
3. 데이터 증강
4. [CLAUDE.md](CLAUDE.md)의 Phase 3 실행

**소요 시간:** 3-5일

---

## 🔍 트러블슈팅

### "레이블이 여전히 나와요"
**해결:** `.env`에서 `USE_CHAT_FORMAT=true` 확인

### "CUDA Out of Memory"
**해결:** `finetune_model_temperature.py`에서
```python
per_device_train_batch_size=1  # 2 → 1
```

### "메시지가 너무 짧아요"
**해결:** `model_server.py`에서
```python
max_new_tokens=60  # 50 → 60
```

### "일관성이 없어요"
**해결:** API 요청 시
```json
{
  "yesterday_temp": 10,
  "today_temp": 20,
  "temperature": 0.3  # 낮을수록 일관적
}
```

---

## 📞 참고 자료

### 파일 위치
- 프롬프트 템플릿: `src/generator/prompt_templates.py`
- 모델 서버: `model_server.py`
- 파인튜닝 스크립트: `scripts/finetune_model_temperature.py`
- 데이터 생성: `scripts/prepare_chat_format_data.py`
- 원본 데이터: `scripts/wrap_temperature_data.py`

### 환경 설정
- `.env.example` - 예시 환경 설정
- `.env` - 실제 사용 (직접 생성)

---

## ⚡ 1분 요약

```bash
# 1. 데이터 생성 (이미 완료!)
python scripts/prepare_chat_format_data.py
# → 302개 학습 + 15개 검증 데이터 생성됨

# 2. 파인튜닝 실행
# finetune_model_temperature.py에서 파일 경로만 수정:
# TRAIN_FILE = "data/train_chat_large.jsonl"
# VAL_FILE = "data/validation_chat_large.jsonl"
python scripts/finetune_model_temperature.py

# 3. 서버 설정
# .env 파일:
# USE_FINETUNED=true
# ADAPTER_PATH=./finetuned_model_chat_large
# USE_CHAT_FORMAT=true

# 4. 실행!
python model_server.py
```

---

## 📝 체크리스트

**시작 전:**
- [ ] GPU 사용 가능 (최소 6GB)
- [ ] Python 3.8+ 설치
- [ ] 필요 라이브러리 설치 (`pip install -r requirements.txt`)
- [ ] 디스크 공간 충분 (10GB+)

**데이터 준비:**
- [x] `data/train_chat_large.jsonl` 생성됨 (302개)
- [x] `data/validation_chat_large.jsonl` 생성됨 (15개)

**파인튜닝:**
- [ ] `finetune_model_temperature.py` 파일 경로 수정
- [ ] 파인튜닝 실행
- [ ] Loss 감소 확인
- [ ] `./finetuned_model_chat_large/` 폴더 생성 확인

**서버 설정:**
- [ ] `.env` 파일 생성 및 설정
- [ ] 서버 정상 시작
- [ ] `/health` 엔드포인트 확인

**테스트:**
- [ ] 기본 테스트 케이스 통과
- [ ] 극한 케이스 테스트
- [ ] 레이블 없이 메시지만 생성됨
- [ ] 40-70자 길이 준수

---

## 🎉 성공 후 다음 단계

### 프로덕션 배포
1. 다양한 엣지 케이스 테스트
2. 응답 시간 최적화
3. 에러 핸들링 강화
4. 모니터링 시스템 구축

### 추가 개선
1. 더 많은 데이터 수집
2. DPO 적용
3. 다른 센서 데이터 통합
4. A/B 테스트

---

**최종 업데이트:** 2025-11-06
**권장 방법:** Chat 형식 302개 데이터 파인튜닝
**예상 소요 시간:** 2-3시간 (파인튜닝 1-2시간 포함)
