# 더 이상 사용하지 않는 파일들 (Deprecated)

## ❌ 규칙 기반 접근 (Phase 0 이전)

Phase 0에서 LLM 중심 파이프라인으로 전환하면서 다음 파일들은 더 이상 사용하지 않습니다.

---

## 1. `scripts/generate_comparison_data.py`

### 문제점:
```python
# 100줄 이상의 if/else 규칙
if abs_diff <= 1:
    messages = ["어제보다 1도 따뜻해졌습니다..."]
elif 2 <= abs_diff <= 4:
    messages = ["어제보다 3도 따뜻해졌습니다..."]
# ... 계속 ...
```

### 대체:
- ✅ `scripts/generate_with_claude.py` 사용
- Claude가 규칙 없이 자연스러운 메시지 생성

---

## 2. `scripts/generate_training_data_manual.py`

### 문제점:
```python
# 카테고리별 if/else 하드코딩
temperature_data = [...]
humidity_data = [...]
combined_data = [...]
# 96개만 수작업 작성
```

### 대체:
- ✅ `scripts/generate_with_claude.py` 사용
- 500개 자동 생성, 더 다양함

---

## 3. `src/generator/output_cleaner.py`

### 문제점:
```python
# 50줄의 regex 규칙
text = re.sub(r'<[^>]+>', '', text)
text = re.sub(r'\?.*$', '', text)
# ... 10개의 regex 규칙 ...
```

### 대체:
- ✅ DPO 학습으로 자동 학습
- ✅ 프롬프트에 "나쁜 예시" 포함
- 모델이 직접 깔끔한 출력 생성

---

## 4. `data/train_merged.jsonl`

### 문제점:
- 규칙 기반으로 생성된 데이터 포함
- 315개는 if/else로 생성됨

### 대체:
- ✅ `data/training_data_claude.jsonl` 사용 (500개)
- ✅ Claude가 생성한 자연스러운 데이터

---

## 🔄 마이그레이션

### Phase 0 이전:
```
학습 데이터 생성:
  generate_training_data_manual.py (96개, if/else)
  + generate_comparison_data.py (315개, if/else)
  = 411개 (규칙 기반)

후처리:
  output_cleaner.py (regex 규칙)
```

### Phase 0 이후:
```
학습 데이터 생성:
  generate_with_claude.py (500개, 규칙 없음)
  + DPO 데이터셋 (16-20쌍)
  = 자연스럽고 다양함

후처리:
  DPO 학습으로 자동 학습
  프롬프트에 "나쁜 예시" 포함
```

---

## 📂 파일 정리

### 보관 (참고용):
```bash
mkdir archive
mv scripts/generate_comparison_data.py archive/
mv scripts/generate_training_data_manual.py archive/
mv data/train_merged.jsonl archive/
mv data/training_data_comparison_fixed.jsonl archive/
```

### 계속 사용:
- ✅ `scripts/generate_with_claude.py`
- ✅ `scripts/generate_dpo_dataset.py`
- ✅ `scripts/finetune_dpo.py` (다음에 작성)
- ✅ `src/generator/prompt_templates.py` (개선된 버전)

---

## 💡 왜 제거하나?

1. **유연성**: 규칙은 새로운 상황에 대응 못함
2. **유지보수**: 100줄 if/else는 수정 어려움
3. **품질**: Claude가 더 자연스러운 표현 생성
4. **확장성**: 새 메시지 타입 추가 시 규칙 안 짜도 됨

---

## ⚠️ 주의

기존 파일들은 삭제하지 말고 `archive/` 폴더에 보관하세요.
나중에 참고할 수 있습니다.
