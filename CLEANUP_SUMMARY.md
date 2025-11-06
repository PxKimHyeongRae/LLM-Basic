# 파일 정리 요약

## 🗂️ Archive로 이동된 파일

### 📁 archive/scripts/ (규칙 기반 & API 스크립트)

**규칙 기반 (if/else) 스크립트:**
- `generate_comparison_data.py` - 100줄 if/else로 온도 메시지 생성
- `generate_training_data_manual.py` - 카테고리별 if/else 데이터 생성 (96개)
- `fix_comparison_data.py` - 규칙 기반 후처리
- `output_cleaner.py` - 50줄 regex 규칙 후처리

**API 기반 스크립트 (참고용):**
- `generate_with_claude.py` - Anthropic API 사용 (로컬 실행용)
- `generate_dpo_dataset.py` - Anthropic API 사용 (로컬 실행용)
- `generate_training_data.py` - OpenRouter API 사용

### 📁 archive/data/ (중간 파일 & 규칙 기반 데이터)

**배치 중간 파일:**
- `training_data_claude_batch1.jsonl` (49줄)
- `training_data_claude_batch2.jsonl` (49줄)
- `training_data_claude_batch3.jsonl` (95줄)
- `training_data_claude_batch4.jsonl` (307줄)
- `training_data_claude_partial.jsonl` (98줄)

**규칙 기반 생성 데이터:**
- `train_merged.jsonl` - 기존 86개 + 규칙 생성 315개 = 401개
- `training_data_comparison.jsonl` - if/else로 생성된 315개
- `training_data_comparison_fixed.jsonl` - 후처리된 버전
- `training_data.jsonl` - 빈 파일

### 📁 archive/docs/ (사용 완료 문서)

- `LOCAL_RUN.md` - 로컬에서 API 실행 가이드 (사용 안 함)
- `PHASE0_INSTRUCTIONS.md` - API 기반 실행 가이드 (사용 안 함)

---

## ✅ 현재 사용 중인 파일

### 📁 scripts/ (활성 스크립트)

- **`finetune_dpo.py`** - ⭐ DPO 학습 (서버에서 실행)
- **`finetune_model.py`** - 일반 파인튜닝
- `evaluate_model.py` - 모델 평가
- `test_finetuned_model.py` - 모델 테스트

### 📁 data/ (활성 데이터)

- **`training_data_claude.jsonl`** - ⭐ 500개 (Claude가 규칙 없이 생성)
- **`dpo_dataset.jsonl`** - ⭐ 16쌍 (chosen/rejected pairs)
- `train.jsonl` - 기존 86개 (참고용)
- `validation.jsonl` - 검증 데이터 10개

### 📄 문서 (활성)

- **`SERVER_GUIDE.md`** - ⭐ 서버 DPO 학습 가이드
- **`README_PHASE0.md`** - ⭐ Phase 0 전체 설명
- `DEPRECATED_FILES.md` - 사용 중단 파일 목록
- `plan.md` - 전체 개선 계획
- `README.md` - 프로젝트 README

---

## 📊 변화 요약

### Before (Phase 0 이전):
```
scripts/
├── generate_comparison_data.py (315개, 100줄 if/else)
├── generate_training_data_manual.py (96개, if/else)
├── output_cleaner.py (50줄 regex)
└── ...

data/
├── train_merged.jsonl (401개, 규칙 기반)
└── ...
```

### After (Phase 0):
```
scripts/
├── finetune_dpo.py ⭐ (규칙 없음, DPO 학습)
└── finetune_model.py

data/
├── training_data_claude.jsonl ⭐ (500개, 규칙 없음)
├── dpo_dataset.jsonl ⭐ (16쌍, 자동 학습)
└── ...

archive/
├── scripts/ (규칙 기반 7개 파일)
├── data/ (중간 파일 9개)
└── docs/ (사용 완료 문서 2개)
```

---

## 🎯 핵심 변화

| 항목 | Before | After |
|------|--------|-------|
| **데이터 생성** | 100줄 if/else 규칙 | Claude가 자연스럽게 생성 |
| **후처리** | 50줄 regex 규칙 | DPO 학습으로 자동 |
| **데이터 개수** | 401개 (규칙 기반) | 500개 (다양성 높음) |
| **유지보수** | 규칙 수정 필요 | 데이터 추가만 |
| **확장성** | 새 상황마다 규칙 추가 | 자동 일반화 |

---

## 📂 Archive 구조

```
archive/
├── data/
│   ├── train_merged.jsonl (401개, 규칙 기반)
│   ├── training_data_comparison.jsonl (315개, if/else)
│   ├── training_data_comparison_fixed.jsonl (후처리)
│   └── training_data_claude_batch*.jsonl (중간 파일 5개)
│
├── scripts/
│   ├── generate_comparison_data.py (100줄 if/else)
│   ├── generate_training_data_manual.py (96개 하드코딩)
│   ├── output_cleaner.py (50줄 regex)
│   ├── fix_comparison_data.py (규칙 기반)
│   ├── generate_with_claude.py (API, 참고용)
│   ├── generate_dpo_dataset.py (API, 참고용)
│   └── generate_training_data.py (OpenRouter API)
│
└── docs/
    ├── LOCAL_RUN.md
    └── PHASE0_INSTRUCTIONS.md
```

---

## ✨ 결과

### 삭제된 코드 라인:
- if/else 규칙: **~150줄**
- regex 규칙: **~50줄**
- 총: **~200줄** 규칙 코드 제거

### 추가된 것:
- Claude 생성 데이터: **500개** (자연스러움)
- DPO 데이터셋: **16쌍** (자동 학습)
- 규칙: **0줄**

---

> 🎯 **"규칙을 짜지 말고, 모델이 학습하게 하자!"**
