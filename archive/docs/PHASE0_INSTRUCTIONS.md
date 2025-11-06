# Phase 0 실행 가이드: 규칙 기반 제거 및 LLM 중심 파이프라인

## 🎯 목표
if/else 규칙 기반 코드를 제거하고, Claude와 DPO를 사용한 LLM 중심 파이프라인으로 전환

---

## 📋 사전 준비

### 1. Anthropic API 키 발급
1. https://console.anthropic.com/ 접속
2. 로그인 후 API Keys 메뉴
3. "Create Key" 클릭하여 API 키 발급
4. 발급된 키를 복사 (sk-ant-로 시작)

### 2. .env 파일에 API 키 추가
```bash
cd ~/lay/llm

# .env 파일 편집
nano .env

# 다음 줄 추가
ANTHROPIC_API_KEY=sk-ant-여기에_발급받은_키_붙여넣기

# 저장: Ctrl+O, Enter, Ctrl+X
```

### 3. Anthropic 패키지 설치
```bash
conda activate ml
pip install anthropic
```

---

## 🚀 Step 1: Claude로 고품질 학습 데이터 생성 (500개)

### 실행:
```bash
cd ~/lay/llm
python scripts/generate_with_claude.py
```

### 예상 소요 시간:
- **5-10분** (Claude API 호출, 배치 처리)
- 500개 온도 시나리오에 대한 메시지 생성
- 규칙 없이 자연스러운 표현

### 출력 파일:
- `data/training_data_claude.jsonl` (약 500개)

### 확인:
```bash
wc -l data/training_data_claude.jsonl
head -n 3 data/training_data_claude.jsonl
```

---

## 🚀 Step 2: DPO 데이터셋 생성 (Chosen/Rejected Pairs)

### 실행:
```bash
python scripts/generate_dpo_dataset.py
```

### 예상 소요 시간:
- **2-3분** (Claude API 호출)
- 기존 나쁜 예시 5개 + 추가 시나리오 11개 = 총 16쌍 생성

### 출력 파일:
- `data/dpo_dataset.jsonl` (약 16쌍)

### 확인:
```bash
wc -l data/dpo_dataset.jsonl
head -n 1 data/dpo_dataset.jsonl | jq .
```

---

## 🚀 Step 3: DPO 학습 실행

### DPO 학습 스크립트 작성 대기 중...
(Claude가 다음에 작성 예정)

### 예상 학습 시간:
- **10-15분** (DPO는 일반 fine-tuning보다 빠름)

---

## 📊 예상 효과

### Before (규칙 기반):
```python
# generate_comparison_data.py
if abs_diff <= 1:
    messages = ["어제보다 1도 따뜻해졌습니다..."]
elif 2 <= abs_diff <= 4:
    messages = ["어제보다 3도 따뜻해졌습니다..."]
# ... 100줄의 if/else

# output_cleaner.py
text = re.sub(r'<[^>]+>', '', text)
text = re.sub(r'\?.*$', '', text)
# ... 10개의 regex 규칙
```

### After (LLM 기반):
```python
# Claude가 자연스럽게 메시지 생성
# 규칙 없음!

# DPO 학습으로 자동으로 깔끔한 출력
# regex 규칙 없음!
```

---

## ✅ 체크리스트

### 사전 준비:
- [ ] Anthropic API 키 발급
- [ ] .env에 API 키 추가
- [ ] anthropic 패키지 설치

### 실행:
- [ ] Step 1: Claude로 500개 데이터 생성
- [ ] Step 2: DPO 데이터셋 생성
- [ ] Step 3: DPO 학습 실행 (스크립트 작성 대기)

### 검증:
- [ ] `data/training_data_claude.jsonl` 생성 확인
- [ ] `data/dpo_dataset.jsonl` 생성 확인
- [ ] 샘플 데이터 품질 확인

---

## 🆘 문제 해결

### API 키 오류:
```
⚠️ ANTHROPIC_API_KEY가 .env에 설정되지 않았습니다.
```
→ .env 파일에 `ANTHROPIC_API_KEY=sk-ant-...` 추가

### 패키지 오류:
```
ModuleNotFoundError: No module named 'anthropic'
```
→ `pip install anthropic` 실행

### API 호출 실패:
- 인터넷 연결 확인
- API 키가 유효한지 확인
- Claude API 사용량 확인 (https://console.anthropic.com/)

---

## 💡 다음 단계

1. ✅ Claude로 고품질 데이터 생성
2. ✅ DPO 데이터셋 생성
3. ⏳ DPO 학습 스크립트 작성
4. ⏳ DPO 학습 실행
5. ⏳ Output cleaning 규칙 제거
6. ⏳ 프롬프트 개선 (나쁜 예시 추가)
7. ⏳ A/B 테스트

---

## 📞 문의

문제가 발생하면 실행 결과를 공유해주세요!
