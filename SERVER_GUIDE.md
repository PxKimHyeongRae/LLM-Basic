# 서버 학습 실행 가이드

## ✅ 로컬에서 완료된 작업

- [x] Claude가 직접 500개 온도 비교 데이터 생성
- [x] DPO 데이터셋 16쌍 생성
- [x] 파일 저장: `data/training_data_claude.jsonl`, `data/dpo_dataset.jsonl`

---

## 📤 Step 1: 서버로 파일 전송

### Windows에서:

```bash
# SCP 사용 (PowerShell 또는 CMD)
cd C:\task\llm

scp data\training_data_claude.jsonl pluxity@서버IP:~/lay/llm/data/
scp data\dpo_dataset.jsonl pluxity@서버IP:~/lay/llm/data/
```

### 또는 WinSCP 사용:
1. WinSCP 실행
2. 서버 접속
3. 로컬: `C:\task\llm\data\`
4. 서버: `~/lay/llm/data/`
5. 두 파일 드래그 앤 드롭

---

## 🎓 Step 2: 서버에서 DPO 학습 실행

### 1. 서버 접속

```bash
ssh pluxity@서버IP
cd ~/lay/llm
```

### 2. 파일 확인

```bash
ls -lh data/training_data_claude.jsonl
ls -lh data/dpo_dataset.jsonl

# 라인 수 확인
wc -l data/training_data_claude.jsonl  # 500줄
wc -l data/dpo_dataset.jsonl           # 16줄
```

### 3. Conda 환경 활성화

```bash
conda activate ml
```

### 4. DPO 학습 실행 (10-15분)

```bash
python scripts/finetune_dpo.py
```

**예상 소요 시간**: 10-15분

**예상 결과**:
```
🚀 DPO 학습 시작
...
✅ DPO 학습 완료! 모델이 ./finetuned_model_dpo에 저장되었습니다.

🎯 효과:
  - 특수 토큰 자동 제거 학습
  - 질문 형식 자동 제거 학습
  - 간결하고 깔끔한 출력 학습
  - Output cleaning 규칙 불필요!
```

### 5. 모델 적용

```bash
# .env 파일 수정
nano .env

# 다음 줄 변경:
# ADAPTER_PATH=./finetuned_model_dpo  로 변경
```

### 6. 모델 서버 재시작

```bash
# 기존 서버 종료
pkill -f model_server.py

# 모델 서버 재시작
python model_server.py
```

---

## 🧪 Step 3: 테스트

### 간단한 테스트:

```bash
# 테스트 파일 있다면
python test_display_message.py
```

### 또는 Python으로 직접 테스트:

```python
import requests

# 테스트 프롬프트
test_cases = [
    {"yesterday": 0, "today": 1},
    {"yesterday": -10, "today": 10},
    {"yesterday": 20, "today": 30},
]

for case in test_cases:
    prompt = f"어제의 평균온도는 {case['yesterday']}도고 오늘의 평균온도는 {case['today']}도야. " \
             f"이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘"

    response = requests.post(
        "http://localhost:8000/generate",
        json={"prompt": prompt, "max_new_tokens": 100}
    )

    result = response.json()
    print(f"\n입력: {case['yesterday']}도 → {case['today']}도")
    print(f"출력: {result['generated_text']}")
```

---

## 📊 예상 결과

### Before (기존 파인튜닝):
```
입력: 0도 → 1도
출력: .<think>...</think>
전광판에 표시할 메시지:
안녕하세요, 오늘 공원은 더 시원합니다...
이 메시지가 적절한가요?
```

### After (DPO 학습):
```
입력: 0도 → 1도
출력: 어제보다 1도 따뜻해졌습니다. 산책하기 좋은 날씨예요.
```

**특징**:
- ✅ 특수 토큰 자동 제거
- ✅ 질문 형식 자동 제거
- ✅ 간결하고 깔끔 (40-70자)
- ✅ 온도 차이 명시
- ✅ 규칙 없이 모델이 학습!

---

## 🆘 문제 해결

### CUDA OOM 에러:

```python
# scripts/finetune_dpo.py 수정
gradient_accumulation_steps=8  # 4 → 8로 증가
per_device_train_batch_size=1  # 유지
```

### "Module 'trl' has no DPOTrainer":

```bash
pip install --upgrade trl
```

### DPO 학습이 너무 오래 걸림:

```python
# scripts/finetune_dpo.py 수정
num_train_epochs=2  # 3 → 2로 감소
```

---

## 📈 성능 비교

### 기존 (401개 규칙 기반 데이터):
- 손실 개선: 94.6% (3.43 → 0.18)
- 문제: 특수 토큰, 질문, 장황함

### Phase 0 (500개 Claude 데이터 + DPO):
- **예상 손실 개선**: 95%+
- **예상 효과**:
  - 특수 토큰 제거 학습
  - 질문 형식 제거 학습
  - 간결성 학습
  - 온도 차이 명시 학습

---

## ✅ 체크리스트

### 전송 전:
- [ ] `data/training_data_claude.jsonl` 존재 (500줄)
- [ ] `data/dpo_dataset.jsonl` 존재 (16줄)

### 서버에서:
- [ ] 파일 전송 확인
- [ ] DPO 학습 실행
- [ ] `finetuned_model_dpo/` 생성 확인
- [ ] .env 수정 (ADAPTER_PATH)
- [ ] 모델 서버 재시작
- [ ] 테스트 실행

---

## 💡 완료 후

테스트 결과를 공유해주세요!

**공유할 내용**:
- 테스트 프롬프트 3-5개
- 각각의 출력 결과
- 개선되었는지 여부

---

> 🎯 **Phase 0 핵심**: 규칙을 짜지 말고, 모델이 학습하게 하자!
