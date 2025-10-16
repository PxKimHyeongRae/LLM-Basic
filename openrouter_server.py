"""
OpenRouter API 서버 - a.py 기반 간단 버전
포트: 8002

사용법:
    python openrouter_server.py
"""

import os
import time
import logging

from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(title="OpenRouter API Server", version="1.0")


class GenerateRequest(BaseModel):
    """텍스트 생성 요청"""
    prompt: str
    model: str = None  # 선택사항


class GenerateResponse(BaseModel):
    """텍스트 생성 응답"""
    generated_text: str
    prompt: str
    generation_time: float
    model: str


@app.on_event("startup")
async def startup_event():
    """서버 시작"""
    logger.info("=" * 70)
    logger.info("OpenRouter API 서버 시작 (포트 8002)")
    logger.info("=" * 70)

    api_key = os.getenv('OPENROUTER_API_KEY', '')
    model = os.getenv('OPENROUTER_MODEL', 'tngtech/deepseek-r1t2-chimera:free')

    if api_key:
        logger.info("✓ API 키 설정됨")
    else:
        logger.warning("⚠️  OPENROUTER_API_KEY가 설정되지 않았습니다!")

    logger.info(f"기본 모델: {model}")
    logger.info("서버 준비 완료!")
    logger.info("=" * 70)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    api_key_set = bool(os.getenv('OPENROUTER_API_KEY'))

    return {
        "message": "OpenRouter API Server",
        "status": "running",
        "api_key_set": api_key_set,
        "model": os.getenv('OPENROUTER_MODEL', 'tngtech/deepseek-r1t2-chimera:free'),
        "port": 8002
    }


@app.get("/health")
async def health():
    """헬스 체크"""
    return {
        "status": "healthy",
        "api_key_set": bool(os.getenv('OPENROUTER_API_KEY'))
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """텍스트 생성 - a.py 방식"""

    # API 키 확인
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENROUTER_API_KEY가 설정되지 않았습니다."
        )

    # 모델 선택
    model = request.model or os.getenv('OPENROUTER_MODEL', 'tngtech/deepseek-r1t2-chimera:free')

    logger.info(f"생성 요청: {len(request.prompt)}자")
    logger.info(f"모델: {model}")

    start_time = time.time()

    try:
        # a.py와 동일한 방식으로 호출
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        completion = client.chat.completions.create(
            extra_body={},
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": request.prompt
                }
            ]
        )

        generated_text = completion.choices[0].message.content
        generation_time = time.time() - start_time

        logger.info(f"✓ 생성 완료 ({generation_time:.2f}초)")

        return GenerateResponse(
            generated_text=generated_text,
            prompt=request.prompt,
            generation_time=generation_time,
            model=model
        )

    except Exception as e:
        logger.error(f"생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('OPENROUTER_SERVER_PORT', 8002))
    logger.info(f"서버를 포트 {port}에서 시작합니다...")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
