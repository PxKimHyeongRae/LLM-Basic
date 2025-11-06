# 전광판 메시지 생성 AI 시범 사업 - 컨텍스트

## 프로젝트 개요

**목적**: IoT 센서 데이터 기반 전광판 메시지 자동 생성
**모델**: KORMo-10B-sft (한국어 대화 최적화 최신 모델)
**환경**: 오프라인 환경 대비 (로컬 모델 필수)
**제약**: AI 시범 사업 - 규칙 기반 처리 불가, 순수 AI만 사용

---

## 현재 상황

### 1. 문제점
모델이 요청한 간단한 메시지 대신 장황한 출력 생성:

```
요청: "어제 10도, 오늘 5도 → 전광판 메시지"

현재 출력:
---
**전광판 메시지:**
오늘 공원은 춥습니다. 겉옷을 챙겨주세요!

(또는)
따뜻하게 입고 오세요!

---
두 문장 모두 자연스럽고 적절하지만, **"오늘은 공원이 춥습니다"**는...

원하는 출력:
어제보다 5도 낮아졌습니다. 외출 시 따뜻하게 입으세요.
```

**근본 원인**: KORMo-10B-sft는 일반 대화에 최적화되어 있어, "간결한 전광판 메시지" 형식에 맞지 않음

### 2. 완료된 작업

#### A. 프롬프트 엔지니어링 개선 ✅
- **파일**: `src/generator/prompt_templates.py:134-179`
- **내용**: 구조화된 프롬프트 (`<instruction>`, `<rules>`, `<examples>`, `<task>`)
- **효과**: 제한적 (10B 모델의 instruction-following 능력 한계)

#### B. Stop Sequences 적용 ✅
- **파일**: `model_server.py:269-307`
- **내용**: `\n\n`, `---`, `**`, `(또는)` 등 불필요한 패턴 감지 시 생성 중단
- **효과**: 너무 긴 출력 방지

#### C. 후처리 로직 구현 (현재 비활성화) ✅
- **파일**: `model_server.py:82-135, 330-333`
- **상태**: 주석처리 (순수 모델 출력 확인용)
- **이유**: AI 시범 사업 제약 - 규칙 기반 불가

#### D. 파인튜닝 준비 스크립트 작성 ✅
1. **소규모 데이터 (45개)**: `scripts/prepare_finetuning_data.py`
   - 온도 비교: 35개
   - 일반 날씨: 10개

2. **대규모 데이터 (300개)**: `scripts/generate_more_training_data.py`
   - 온도 변화: 200개
   - 극한 날씨: 50개
   - 날씨 조건: 50개

3. **파인튜닝 스크립트**: `scripts/finetune_model_v2.py`
   - QLoRA 방식 (4-bit 양자화)
   - LoRA rank: 32
   - Epoch: 5
   - Learning rate: 3e-4

### 3. 현재 설정

**모델**: KORMo-10B-sft
**양자화**: 4-bit (~6GB 메모리)
**파인튜닝**: 미실행
**후처리**: 비활성화

---

## 앞으로 해야 할 일

### Phase 1: 파인튜닝 실행 (1-2일)

#### Step 1: 학습 데이터 생성
```bash
# 대규모 데이터 생성 (300개)
python scripts/generate_more_training_data.py
```

**예상 결과**:
- `data/train_large.jsonl`: ~270개
- `data/validation_large.jsonl`: ~30개

**중요**: 데이터가 많을수록 파인튜닝 효과 증가

#### Step 2: 파인튜닝 실행
```bash
# 기존 스크립트 수정 필요 (train_large.jsonl 사용)
python scripts/finetune_model_v2.py
```

**수정 필요 사항** (`finetune_model_v2.py`):
```python
# Line 25-26 변경
TRAIN_FILE = "data/train_large.jsonl"  # train_structured.jsonl → train_large.jsonl
VAL_FILE = "data/validation_large.jsonl"  # validation_structured.jsonl → validation_large.jsonl
```

**예상 시간**: 1-2시간 (GPU 성능에 따라)
**저장 위치**: `./finetuned_model_v2/`

#### Step 3: 파인튜닝 모델 적용
```bash
# .env 파일 수정
USE_FINETUNED=true
ADAPTER_PATH=./finetuned_model_v2

# 서버 재시작
python model_server.py
```

#### Step 4: 성능 평가
테스트 케이스로 품질 확인:
- 온도 비교 (어제 vs 오늘)
- 극한 날씨 (폭염, 한파)
- 일반 날씨 조건

### Phase 2: 성능 개선 (필요시)

#### Option A: 데이터 증강
- 현재 300개 → 500-1000개로 확장
- 실제 사용 케이스 추가
- 다양한 표현 방식 추가

#### Option B: 하이퍼파라미터 튜닝
```python
# finetune_model_v2.py 수정
num_train_epochs=10  # 5 → 10
learning_rate=2e-4   # 3e-4 → 2e-4 (더 안정적)
lora_r=64           # 32 → 64 (더 많은 파라미터)
```

#### Option C: DPO (Direct Preference Optimization)
- 좋은 메시지 vs 나쁜 메시지 쌍 학습
- 더 정교한 출력 제어 가능
- `scripts/finetune_dpo.py` 활용

**DPO 데이터 예시**:
```json
{
  "prompt": "어제 10도, 오늘 5도",
  "chosen": "어제보다 5도 낮아졌습니다. 외출 시 따뜻하게 입으세요.",
  "rejected": "---\n**전광판 메시지:**\n오늘은 춥습니다...(또는)..."
}
```

### Phase 3: 프로덕션 준비

#### 안정성 테스트
- 다양한 엣지 케이스 테스트
- 응답 시간 측정
- 메모리 사용량 모니터링

#### 백업 전략
- 파인튜닝 실패 시 원본 모델로 폴백
- 여러 버전의 파인튜닝 모델 유지

---

## 기술적 제약사항

### 불가능한 접근 방법
❌ **OpenRouter API 등 온라인 모델** - 오프라인 환경 대비 필요
❌ **규칙 기반 후처리** - AI 시범 사업 제약
❌ **모델 교체** - KORMo-10B는 한국어 최적화 최신 모델

### 가능한 접근 방법
✅ **파인튜닝** - 모델을 태스크에 맞게 학습
✅ **프롬프트 엔지니어링** - 입력 형식 최적화
✅ **Stop Sequences** - 생성 중단 조건 설정
✅ **데이터 증강** - 더 많은 학습 데이터

---

## 예상 결과

### Before 파인튜닝
- 장황한 출력 (마크다운, 설명, 대안 제시)
- 형식 불일치
- 온도 정보 누락 가능

### After 파인튜닝 (300개 데이터)
- 간결한 한 문장 출력
- 일관된 형식
- 필수 정보 포함 (온도 차이 명시)
- 적절한 조언 포함

### After 파인튜닝 + DPO
- 완벽한 형식 제어
- 높은 품질 일관성
- 다양한 상황 대응

---

## 다음 실행 명령어

```bash
# 1. 순수 온도 비교 데이터 생성
python scripts/generate_temperature_dataset.py

# 2. 파인튜닝 실행
python scripts/finetune_model_temperature.py

# 3. .env 설정 변경
# USE_FINETUNED=true
# ADAPTER_PATH=./finetuned_model_temperature

# 4. 서버 재시작
python model_server.py

# 5. 테스트
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{"yesterday_temp": 35, "today_temp": 25}'
```

---

## 성공 지표

✅ **출력 형식**: 한 문장, 마크다운 없음, 레이블 없음
✅ **정보 완전성**: 온도 차이 명시, 적절한 조언
✅ **길이**: 40-70자
✅ **일관성**: 동일 입력에 유사한 출력
✅ **응답 시간**: 15초 이내

---

## 참고 파일

- **프롬프트 템플릿**: `src/generator/prompt_templates.py`
- **모델 서버**: `model_server.py`
- **데이터 생성**: `scripts/generate_more_training_data.py`
- **파인튜닝**: `scripts/finetune_model_v2.py`
- **환경 설정**: `.env` (`.env.example` 참고)
- **개선 가이드**: `IMPROVEMENT_GUIDE.md`

---

## 마지막 업데이트
2025-11-05

## 현재 단계
Phase 2 - 공원 특화 대량 데이터 파인튜닝 준비

### 최신 개선사항 (2025-11-05 최종)

#### LLM이 직접 작성한 자연스러운 학습 데이터 ✅
- **방식**: 온도 범위별, 변화 패턴별로 Claude가 직접 메시지 작성
- **입력**: `yesterday_temp`, `today_temp` 두 값만 사용 (순수 온도 비교)
- **제외**: 폭염, 한파, 일교차 등 특수 조건 제거 (실제 사용 케이스에 집중)

#### 공원 특화 메시지 ✅
- **일반**: "외출 시 따뜻하게 입으세요" ❌
- **공원**: "공원 산책 시 겉옷 챙기세요" ✅
- **공원 요소**: 산책, 조깅, 운동, 벤치, 산책로, 분수대 등 포함

#### 온도 절대값 + 변화량 모두 고려 ✅
- 35도 → 25도: "시원해졌습니다. 공원 산책 최고예요" (논리적)
- 25도 → 35도: "더워졌습니다. 공원 그늘에서 휴식하세요" (논리적)
- 10도 → 5도: "춥습니다. 따뜻하게 입고 짧은 산책 추천합니다" (논리적)
- 0도 → 12도: "포근해졌습니다. 공원을 걸어보세요" (논리적)

#### 학습 데이터 구성 ✅
**온도 변화 패턴별 분류**:
- 큰 상승 (10도 이상): 20개
- 중간 상승 (5-10도): 20개
- 작은 상승 (1-5도): 20개
- 변화 거의 없음 (±0-2도): 11개
- 작은 하강 (1-5도): 20개
- 중간 하강 (5-10도): 16개
- 큰 하강 (10도 이상): 12개

**총 데이터**: ~120개 (자연스럽고 논리적인 메시지)
