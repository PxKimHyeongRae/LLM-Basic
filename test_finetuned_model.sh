#!/bin/bash

echo "========================================"
echo "파인튜닝 모델 테스트"
echo "========================================"

echo ""
echo "테스트 1: 온도 하강 (어제 10도 → 오늘 5도)"
echo "----------------------------------------"
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{
    "yesterday_temp": 10,
    "today_temp": 5,
    "max_new_tokens": 50,
    "temperature": 0.7
  }' | jq -r '.generated_text'

echo ""
echo ""
echo "테스트 2: 온도 상승 (어제 5도 → 오늘 20도)"
echo "----------------------------------------"
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{
    "yesterday_temp": 5,
    "today_temp": 20,
    "max_new_tokens": 50,
    "temperature": 0.7
  }' | jq -r '.generated_text'

echo ""
echo ""
echo "테스트 3: 큰 온도 하강 (어제 30도 → 오늘 10도)"
echo "----------------------------------------"
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{
    "yesterday_temp": 30,
    "today_temp": 10,
    "max_new_tokens": 50,
    "temperature": 0.7
  }' | jq -r '.generated_text'

echo ""
echo ""
echo "테스트 4: 작은 온도 변화 (어제 18도 → 오늘 20도)"
echo "----------------------------------------"
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{
    "yesterday_temp": 18,
    "today_temp": 20,
    "max_new_tokens": 50,
    "temperature": 0.7
  }' | jq -r '.generated_text'

echo ""
echo ""
echo "테스트 5: 비슷한 온도 (어제 15도 → 오늘 16도)"
echo "----------------------------------------"
curl -X POST "http://localhost:8000/generate/temperature" \
  -H "Content-Type: application/json" \
  -d '{
    "yesterday_temp": 15,
    "today_temp": 16,
    "max_new_tokens": 50,
    "temperature": 0.7
  }' | jq -r '.generated_text'

echo ""
echo "========================================"
echo "테스트 완료"
echo "========================================"
