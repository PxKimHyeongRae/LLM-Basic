# 전광판 메시지 생성 모델 성능 개선 계획

## 📊 현재 문제 분석

### 1. 출력 품질 문제
- ❌ `<think>`, `</think>` 같은 특수 토큰 출력
- ❌ 불필요한 설명과 질문 추가 ("이 메시지가 적절한가요?")
- ❌ 너무 장황함 (전광판에 부적합)
- ❌ 온도 차이를 명확히 언급하지 않음
- ❌ 일관성 없는 출력 길이

### 2. 테스트 결과 분석

| 입력 | 현재 출력 | 원하는 출력 | 문제점 |
|------|----------|------------|--------|
| 0°C → 1°C | "더 시원합니다" (반대) | "어제보다 더 덥습니다" | ❌ 반대 의미 |
| -10°C → 10°C | 장황한 설명 + 질문 | "20도 따뜻해졌어요" | ❌ 온도차 미언급 |
| 10°C → -10°C | 장황 + "난방 안내" | "20도 이하로 추워요" | ❌ 관련없는 정보 |
| 20°C → 30°C | ✅ 대체로 좋음 | "10도 상승, 물 섭취" | ✅ 거의 정확 |
| 30°C → 20°C | 질문 형식 | "10도 하강, 감기 조심" | ❌ 온도차 미언급 |

### 3. 학습 데이터 부족
- 현재: 96개 (너무 적음)
- 필요: 300-500개 이상
- 비교 메시지 데이터: 5개만 존재 → 매우 부족

---

## 🎯 개선 목표

### 핵심 요구사항
1. **간결성**: 40-70자 이내
2. **명확성**: 온도 차이를 숫자로 명시
3. **깔끔함**: 특수문자, 이모지, 불필요한 질문 제거
4. **일관성**: 같은 형식으로 출력
5. **정확성**: 온도 증감 방향 정확히 표현

### 출력 포맷 표준화
```
[상황 설명] + [구체적 온도 차이] + [행동 권고]

예시:
- "어제보다 10도 따뜻해졌습니다. 가벼운 옷차림을 권장합니다."
- "어제보다 20도 추워졌습니다. 따뜻하게 입고 외출하세요."
```

---

## 📋 단계별 개선 계획

## ⚡ Phase 0: 규칙 기반 제거 및 LLM 중심 파이프라인 (최우선, 즉시 실행)

### 🎯 핵심 철학
**"규칙을 짜지 말고, 모델이 학습하게 하자"**

현재 문제점:
- ❌ `generate_comparison_data.py`: if/else로 온도 구간별 메시지 하드코딩
- ❌ `generate_training_data_manual.py`: if/else로 카테고리별 메시지 하드코딩
- ❌ `output_cleaner.py`: regex/if/else로 후처리 룰 하드코딩

→ **유연성 부족, 확장 어려움, 새로운 상황 대응 불가**

### 0.1 Claude 기반 고품질 학습 데이터 생성 (규칙 없이)

**목적**: if/else 없이 자연스럽고 다양한 메시지 생성

**기존 방식 (규칙 기반):**
```python
if abs_diff <= 1:
    messages = ["어제보다 1도 따뜻해졌습니다..."]
elif 2 <= abs_diff <= 4:
    messages = ["어제보다 3도 따뜻해졌습니다..."]
# 100줄의 if/else...
```

**새로운 방식 (LLM 기반):**
```python
# Claude에게 한 번에 요청
prompt = """
다음 온도 변화 시나리오에 대해 전광판 메시지를 생성하세요.

요구사항:
- 40-70자 이내
- 온도 차이 숫자 명시
- 자연스러운 한국어
- "어제보다" 표현 사용

시나리오 100개를 생성하고 JSON 형식으로 반환:
{yesterday: -15, today: -10, message: "..."}
"""

# Claude가 다양하고 자연스러운 메시지 생성
# 규칙 없이 패턴 학습
```

**구현:**
1. Claude API를 이용한 대량 데이터 생성 스크립트
2. 온도 시나리오 500개 생성 (규칙 없이 다양성 확보)
3. Claude가 자연스러운 표현 생성

### 0.2 DPO 데이터셋 생성 (Good vs Bad 예시)

**목적**: 규칙 없이 "좋은 출력"을 학습

**데이터 형식:**
```json
{
  "prompt": "어제 0도, 오늘 1도",
  "chosen": "어제보다 1도 따뜻해졌습니다. 산책하기 좋은 날씨예요.",
  "rejected": "<think>음.. 1도 차이니까...</think>\n전광판에 표시할 메시지:\n\n안녕하세요, 오늘 공원은 더 시원합니다. 외출 시 가벼운 겉옷을 챙기세요. 감사합니다. 2월 5일 (화요일) 오전 9시 38분\n\n이 메시지가 적절한가요?"
}
```

**생성 방법:**
1. 기존 모델로 100개 프롬프트 실행 (나쁜 예시 수집)
2. Claude가 같은 프롬프트에 대해 좋은 예시 생성
3. 100쌍의 chosen/rejected 데이터 생성

**효과:**
- 규칙 없이 "특수 토큰 제거", "질문 제거" 등을 학습
- 모델이 자동으로 깔끔한 출력 생성

### 0.3 Output Cleaning을 프롬프트/학습으로 대체

**기존 방식 (제거 대상):**
```python
# output_cleaner.py - 50줄의 regex 규칙
text = re.sub(r'<[^>]+>', '', text)
text = re.sub(r'\?.*$', '', text)
# ... 10개의 regex 규칙
```

**새로운 방식 1: 프롬프트 개선**
```python
# 모델에게 직접 요구
prompt = """아래 입력을 공원 전광판에 표시할 메시지로 변환하세요.

중요: 특수문자, 질문, 메타 설명 없이 바로 메시지만 출력하세요.

나쁜 예시:
- "<think>...</think> 전광판에 표시할 메시지: 오늘은..."
- "오늘은 따뜻합니다. 이 메시지가 적절한가요?"

좋은 예시:
- "어제보다 10도 따뜻해졌습니다. 가벼운 옷차림을 권장합니다."

입력: {input}
출력:"""
```

**새로운 방식 2: DPO 학습**
- chosen/rejected 쌍으로 학습하면 자동으로 깔끔한 출력
- 규칙 없이 모델이 패턴 학습

### 0.4 Claude 평가 루프 (자동 품질 관리)

**목적**: 규칙 없이 품질 평가 및 개선

**구현:**
```python
# scripts/claude_evaluation_loop.py

def evaluate_with_claude(outputs):
    """Claude가 출력 품질 평가"""
    prompt = f"""
    다음 전광판 메시지들을 평가하세요 (1-5점):

    평가 기준:
    - 40-70자 이내인가?
    - 온도 차이를 숫자로 언급하는가?
    - 특수문자나 질문이 없는가?
    - 자연스러운 한국어인가?

    출력: {outputs}

    각 메시지에 점수와 개선 이유를 JSON으로 반환:
    {{"score": 3, "reason": "...", "improved": "..."}}
    """

    return claude_api_call(prompt)

# 자동 개선 루프
for iteration in range(5):
    outputs = model.generate(test_prompts)
    evaluations = evaluate_with_claude(outputs)

    # 낮은 점수만 개선
    low_quality = [e for e in evaluations if e['score'] < 4]
    improved_data = [(prompt, e['improved']) for e in low_quality]

    # 개선 데이터로 재학습
    finetune_with_new_data(improved_data)
```

**효과:**
- 규칙 없이 Claude가 품질 판단
- 자동으로 데이터 개선 및 재학습
- 5번 반복하면 점진적 품질 향상

---

## Phase 1: DPO 학습 및 적용 (1-2일)

### 1.1 DPO 학습 실행
**목적**: Chosen/Rejected 쌍으로 선호도 학습

**현재 프롬프트:**
```
어제의 평균온도는 {yesterday}도고 오늘의 평균온도는 {today}도야.
이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘
```

**개선된 프롬프트:**
```
아래 입력을 공원 전광판에 표시할 짧은 메시지로 변환하세요.

규칙:
1. 40-70자 이내로 작성
2. 온도 차이를 숫자로 명시 (예: "10도 따뜻", "5도 추움")
3. 특수문자, 이모지, 질문 금지
4. 한 문장으로 완결
5. "어제보다" 표현 필수

입력: 어제 {yesterday}도, 오늘 {today}도
출력:
```

### 1.2 Post-processing 필터 추가
**목적**: 출력 후처리로 불필요한 내용 제거

**구현:**
```python
def clean_output(text):
    # 특수 토큰 제거
    text = re.sub(r'<[^>]+>', '', text)

    # 질문 제거
    text = re.sub(r'\?.*$', '', text)

    # 첫 문장만 추출
    text = text.split('.')[0].strip() + '.'

    # 이모지 제거
    text = re.sub(r'[^\w\s.,!?°℃\-]', '', text)

    # 길이 제한 (70자)
    if len(text) > 70:
        text = text[:67] + '...'

    return text
```

### 1.3 학습 데이터 대폭 확장
**목적**: 온도 비교 데이터 집중 보강

**추가 데이터:**
- 온도 비교 시나리오: 200개 (현재 5개 → 205개)
- 다양한 온도 차이: 1도 차이부터 30도 차이까지
- 계절별 변화: 봄/가을 일교차, 여름/겨울 극단적 변화

**데이터 생성 스크립트 수정:**
```python
# scripts/generate_comparison_data.py
for temp_diff in range(-30, 31):  # -30도 ~ +30도 차이
    for base_temp in [-10, 0, 10, 20, 30]:
        yesterday = base_temp
        today = base_temp + temp_diff

        # 다양한 표현 생성
        ...
```

---

## Phase 2: 중기 개선 (3-7일)

### 2.1 DPO (Direct Preference Optimization) 적용
**목적**: 좋은 답변 vs 나쁜 답변 학습

**DPO란?**
- RLHF의 간소화 버전
- 선호하는 답변과 비선호 답변 쌍을 학습
- Reward Model 불필요 (단순함)

**데이터 형식:**
```json
{
  "prompt": "어제 0도, 오늘 1도",
  "chosen": "어제보다 1도 따뜻해졌습니다. 산책하기 좋은 날씨예요.",
  "rejected": "전광판에 표시할 메시지:\n\n안녕하세요, 오늘 공원은 더 시원합니다..."
}
```

**구현:**
1. 현재 모델 출력 수집 (100개)
2. 수동으로 좋은/나쁜 답변 라벨링
3. DPO 라이브러리 사용하여 재학습

**예상 효과:**
- 출력 스타일 일관성 70% → 95%
- 불필요한 내용 50% 감소

### 2.2 Few-Shot Learning 적용
**목적**: 예시를 통해 학습

**프롬프트에 예시 추가:**
```
예시 1:
입력: 어제 20도, 오늘 30도
출력: 어제보다 10도 상승해 매우 덥습니다. 물을 충분히 마시세요.

예시 2:
입력: 어제 10도, 오늘 -10도
출력: 어제보다 20도 하강해 매우 춥습니다. 따뜻한 옷을 입으세요.

예시 3:
입력: 어제 {yesterday}도, 오늘 {today}도
출력:
```

### 2.3 재파인튜닝 (300개 데이터)
**목적**: 확장된 데이터로 재학습

**설정:**
- Epoch: 5 (3 → 5)
- 학습률: 1e-4 (더 안정적)
- Batch size: 2
- 온도 비교 데이터 집중

---

## Phase 3: 장기 개선 (1-2주)

### 3.1 RLHF 완전 구현
**목적**: 사용자 피드백 기반 강화학습

**단계:**
1. **Reward Model 학습**
   - 좋은 답변: +1점
   - 나쁜 답변: -1점
   - 중간 답변: 0점

2. **PPO (Proximal Policy Optimization)**
   - 모델이 reward를 최대화하도록 학습
   - 너무 극단적으로 변하지 않도록 제약

3. **사용자 피드백 수집 시스템**
   ```python
   # 웹 인터페이스 추가
   @app.post("/feedback")
   def submit_feedback(message: str, rating: int):
       # rating: 1-5 (1=나쁨, 5=좋음)
       save_feedback(message, rating)
   ```

4. **주기적 재학습**
   - 매주 피드백 데이터 수집
   - 월 1회 재파인튜닝

### 3.2 대화형 개선 루프
**목적**: Claude와 모델이 대화하며 개선

**프로세스:**
1. Claude가 100개 프롬프트 생성
2. 모델이 답변 생성
3. Claude가 답변 평가 (1-5점)
4. 낮은 점수 답변 개선
5. 개선된 데이터로 재학습
6. 반복

**자동화 스크립트:**
```python
# scripts/iterative_improvement.py
for iteration in range(10):
    # 1. 프롬프트 생성
    prompts = generate_test_cases(100)

    # 2. 모델 출력
    outputs = model.generate(prompts)

    # 3. Claude 평가 (API)
    scores = claude_evaluate(outputs)

    # 4. 낮은 점수만 개선
    low_score_data = filter(scores < 3)
    improved = claude_improve(low_score_data)

    # 5. 재학습
    finetune(improved)
```

### 3.3 Ensemble 모델
**목적**: 여러 모델의 장점 결합

**구성:**
- 모델 A: 온도 비교 특화
- 모델 B: 간결성 특화
- 모델 C: 안전 메시지 특화

**추론 시:**
```python
output_a = model_a.generate(prompt)
output_b = model_b.generate(prompt)
output_c = model_c.generate(prompt)

# 투표 또는 평균
final = ensemble_vote([output_a, output_b, output_c])
```

---

## 📈 평가 지표

### 자동 평가
```python
def evaluate(output, expected):
    scores = {
        'length': check_length(output, 40, 70),        # 40-70자
        'temp_diff': has_temperature_diff(output),     # 온도차 언급
        'clean': no_special_chars(output),             # 특수문자 없음
        'complete': is_complete_sentence(output),      # 완결된 문장
        'relevant': is_relevant(output, expected),     # 관련성
    }
    return sum(scores.values()) / len(scores)
```

### 수동 평가 (주 1회)
- 20개 샘플 검토
- A/B/C 등급 부여
- 피드백 데이터베이스 저장

---

## 🛠️ 구현 우선순위

### 🔥 긴급 (이번 주)
1. ✅ Post-processing 필터 추가 → `src/generator/output_cleaner.py`
2. ✅ 프롬프트 개선 → `src/generator/prompt_templates.py`
3. ✅ 온도 비교 데이터 200개 추가 → `scripts/generate_comparison_data.py`

### 🚀 중요 (다음 주)
4. ⏳ DPO 데이터셋 준비 (100쌍)
5. ⏳ Few-shot 프롬프트 적용
6. ⏳ 재파인튜닝 (300개 데이터)

### 💡 추후 (2주차)
7. ⏳ RLHF 파이프라인 구축
8. ⏳ 자동 평가 시스템
9. ⏳ 대화형 개선 루프

---

## 📊 예상 성능 개선

| 단계 | 방법 | 예상 정확도 | 소요 시간 |
|------|------|------------|----------|
| 현재 | 96개 데이터 | 60% | - |
| Phase 1 | 프롬프트 + 필터 + 300개 데이터 | 75% | 2일 |
| Phase 2 | DPO + Few-shot | 85% | 1주 |
| Phase 3 | RLHF + Ensemble | 95% | 2주 |

---

## 🔄 지속적 개선 프로세스

### 주간 루틴
- 월요일: 사용자 피드백 분석
- 수요일: 새 데이터 생성 및 검증
- 금요일: 재파인튜닝 및 배포

### 월간 루틴
- 1주차: 성능 평가 리포트
- 2주차: 새로운 개선 기법 실험
- 3주차: 대규모 재학습
- 4주차: A/B 테스트

---

## 💬 Claude와의 협업 방식

### 1. 데이터 품질 검증
```
Claude: "이 데이터가 적절한지 평가해줘"
Model: [100개 출력]
Claude: [각 출력 평가] → 개선안 제시
```

### 2. 프롬프트 최적화
```
Claude: "이 프롬프트로 테스트"
Model: [출력]
Claude: "더 나은 프롬프트 제안" → 반복
```

### 3. 엣지 케이스 발견
```
Claude: "실패할 만한 케이스 생성"
Model: [출력]
Claude: [문제 분석] → 개선 데이터 추가
```

---

## 📝 다음 액션 아이템

### 즉시 실행 (오늘)
- [ ] `output_cleaner.py` 작성
- [ ] 프롬프트 개선 적용
- [ ] 온도 비교 데이터 생성 스크립트 작성

### 내일 실행
- [ ] 200개 비교 데이터 생성
- [ ] 재파인튜닝 실행
- [ ] 개선 전후 A/B 테스트

### 이번 주
- [ ] DPO 데이터셋 준비 시작
- [ ] Few-shot 프롬프트 실험
- [ ] 자동 평가 시스템 초안

---

## 🎯 최종 목표

**완벽한 전광판 메시지 생성 시스템:**
1. ✅ 100% 간결 (40-70자)
2. ✅ 100% 정확 (온도 차이 명시)
3. ✅ 100% 깔끔 (특수문자 없음)
4. ✅ 95% 일관성 (같은 형식)
5. ✅ 사용자 만족도 90% 이상

**예상 완료 시점:** 2주 후

---

> 💡 **핵심 전략**: 작은 개선을 빠르게 반복하며, Claude와 모델이 협업하여 지속적으로 품질을 향상시킨다.
