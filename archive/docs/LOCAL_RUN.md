# 로컬(Windows)에서 Claude로 데이터 생성하기

## 🎯 목표
로컬에서 Claude API로 500개 데이터 생성 → 파일로 저장 → 서버로 전송 → 서버에서 학습

---

## 📋 Step 1: Anthropic API 키 설정 (1분)

### 1. API 키 발급
- https://console.anthropic.com/ 접속
- 로그인 후 "API Keys" 메뉴
- "Create Key" 클릭하여 발급
- `sk-ant-`로 시작하는 키 복사

### 2. .env 파일에 추가
```bash
# C:\task\llm\.env 파일 열기
# 다음 줄 추가:
ANTHROPIC_API_KEY=sk-ant-여기에_발급받은_키_붙여넣기
```

### 3. Python 패키지 설치
```bash
# 명령 프롬프트 또는 PowerShell
cd C:\task\llm
pip install anthropic
```

---

## 📋 Step 2: Claude로 500개 데이터 생성 (5-10분)

### 실행:
```bash
python scripts\generate_with_claude.py
```

### 결과:
- `data\training_data_claude.jsonl` 생성 (약 500개)

---

## 📋 Step 3: DPO 데이터셋 생성 (2-3분)

### 실행:
```bash
python scripts\generate_dpo_dataset.py
```

### 결과:
- `data\dpo_dataset.jsonl` 생성 (약 16-20쌍)

---

## 📋 Step 4: 생성된 파일 확인

```bash
# 라인 수 확인
python -c "with open('data/training_data_claude.jsonl', encoding='utf-8') as f: print(len(f.readlines()), 'lines')"

python -c "with open('data/dpo_dataset.jsonl', encoding='utf-8') as f: print(len(f.readlines()), 'lines')"

# 샘플 확인
python -c "import json; f = open('data/training_data_claude.jsonl', encoding='utf-8'); print(json.loads(f.readline()))"
```

---

## 📋 Step 5: 서버로 파일 전송

### 방법 1: SCP 사용 (Linux/Mac/Windows with OpenSSH)
```bash
scp data\training_data_claude.jsonl pluxity@서버IP:~/lay/llm/data/
scp data\dpo_dataset.jsonl pluxity@서버IP:~/lay/llm/data/
```

### 방법 2: WinSCP (Windows GUI)
1. WinSCP 실행
2. 서버 접속
3. 로컬: `C:\task\llm\data\`
4. 서버: `~/lay/llm/data/`
5. 파일 드래그 앤 드롭:
   - `training_data_claude.jsonl`
   - `dpo_dataset.jsonl`

### 방법 3: 수동 복사 (텍스트 에디터)
파일 크기가 작으면 파일 내용을 복사해서 서버에서 직접 생성

---

## 📋 Step 6: 서버에서 학습 실행

서버에 접속한 후:
```bash
cd ~/lay/llm

# 파일 확인
ls -lh data/training_data_claude.jsonl
ls -lh data/dpo_dataset.jsonl

# DPO 학습 실행 (스크립트는 다음 단계에서 생성)
python scripts/finetune_dpo.py
```

---

## ✅ 체크리스트

- [ ] Anthropic API 키 발급
- [ ] .env에 API 키 추가
- [ ] `pip install anthropic` 실행
- [ ] `training_data_claude.jsonl` 생성 (500개)
- [ ] `dpo_dataset.jsonl` 생성 (16-20쌍)
- [ ] 파일 내용 확인
- [ ] 서버로 파일 전송
- [ ] 서버에서 파일 확인

---

## 💡 완료 후

로컬에서 데이터 생성이 완료되고 서버로 전송이 끝나면,
"완료했어"라고 알려주세요. 그러면 DPO 학습 스크립트를 작성하겠습니다.
