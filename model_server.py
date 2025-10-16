"""
KORMo 모델 서버 - FastAPI 기반
모델을 한 번만 로드하고 HTTP API로 요청을 받아 처리합니다.

사용법:
    # 서버 시작
    python model_server.py

    # 또는 uvicorn으로 직접 실행
    uvicorn model_server:app --host 0.0.0.0 --port 8000
"""

import os
import gc
import time
from typing import Dict, Optional
import logging

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
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
app = FastAPI(title="KORMo Model Server", version="1.0")

# 전역 변수로 모델과 토크나이저 저장
model = None
tokenizer = None
model_loaded = False


class GenerateRequest(BaseModel):
    """텍스트 생성 요청 스키마"""
    prompt: str
    max_new_tokens: int = 50
    temperature: float = 0.5
    top_p: float = 0.85
    repetition_penalty: float = 1.2
    do_sample: bool = True


class GenerateResponse(BaseModel):
    """텍스트 생성 응답 스키마"""
    generated_text: str
    prompt: str
    generation_time: float


def load_model():
    """모델과 토크나이저를 로드합니다."""
    global model, tokenizer, model_loaded

    if model_loaded:
        logger.info("모델이 이미 로드되어 있습니다.")
        return

    try:
        model_path = os.getenv('MODEL_PATH', 'KORMo-Team/KORMo-10B-sft')
        quantization_type = os.getenv('QUANTIZATION', '8bit').lower()

        logger.info("=" * 70)
        logger.info(f"모델 로드 시작: {model_path}")
        logger.info(f"양자화 타입: {quantization_type}")
        logger.info("=" * 70)

        # GPU 메모리 정리
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("✓ GPU 메모리 정리 완료")

        # 토크나이저 로드
        logger.info("토크나이저 로드 중...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        logger.info("✓ 토크나이저 로드 완료")

        # 양자화 설정
        quantization_config = None
        if torch.cuda.is_available() and quantization_type in ['4bit', '8bit']:
            if quantization_type == '4bit':
                logger.info("4bit 양자화 설정 중...")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )
            elif quantization_type == '8bit':
                logger.info("8bit 양자화 설정 중...")
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                )

        # 모델 로드
        logger.info("모델 로드 중... (10분 정도 소요)")
        start_time = time.time()

        if torch.cuda.is_available() and quantization_config:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                quantization_config=quantization_config,
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
        elif torch.cuda.is_available():
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float32,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            model = model.to('cpu')

        model.eval()

        elapsed = time.time() - start_time
        logger.info(f"✓ 모델 로드 완료! (소요 시간: {elapsed:.1f}초)")
        logger.info("=" * 70)

        model_loaded = True

    except Exception as e:
        logger.error(f"모델 로드 실패: {e}", exc_info=True)
        raise


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 로드"""
    logger.info("서버 시작 중...")
    load_model()
    logger.info("서버 준비 완료! API 요청을 받을 수 있습니다.")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "KORMo Model Server",
        "status": "running" if model_loaded else "loading",
        "model_loaded": model_loaded
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy" if model_loaded else "loading",
        "model_loaded": model_loaded,
        "cuda_available": torch.cuda.is_available()
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """텍스트 생성 엔드포인트"""
    if not model_loaded:
        raise HTTPException(status_code=503, detail="모델이 아직 로드 중입니다.")

    try:
        logger.info(f"생성 요청 받음: {len(request.prompt)} 글자")
        start_time = time.time()

        # 토큰화
        inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device)

        # 생성
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=request.do_sample,
                repetition_penalty=request.repetition_penalty,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                early_stopping=True
            )

        # 디코딩
        full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # 프롬프트 제거
        generated_text = full_output[len(request.prompt):].strip()

        generation_time = time.time() - start_time

        logger.info(f"✓ 생성 완료 (소요 시간: {generation_time:.2f}초)")

        return GenerateResponse(
            generated_text=generated_text,
            prompt=request.prompt,
            generation_time=generation_time
        )

    except Exception as e:
        logger.error(f"생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"생성 실패: {str(e)}")


@app.post("/reload")
async def reload_model():
    """모델 재로드 (메모리 정리 후 다시 로드)"""
    global model, tokenizer, model_loaded

    logger.info("모델 재로드 요청...")

    # 기존 모델 언로드
    if model is not None:
        del model
        del tokenizer
        model = None
        tokenizer = None
        model_loaded = False

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("기존 모델 언로드 완료")

    # 모델 재로드
    load_model()

    return {"status": "success", "message": "모델이 재로드되었습니다."}


if __name__ == "__main__":
    import uvicorn

    # 포트 설정
    port = int(os.getenv('MODEL_SERVER_PORT', 8000))

    logger.info(f"모델 서버를 포트 {port}에서 시작합니다...")

    # 서버 실행
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
