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
import re
from typing import Dict, Optional, List
import logging

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, StoppingCriteria, StoppingCriteriaList
from peft import PeftModel
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import sys
sys.path.append('.')
from src.generator.prompt_templates import PromptTemplates

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


class TemperatureComparisonRequest(BaseModel):
    """온도 비교 메시지 생성 요청 스키마"""
    yesterday_temp: float
    today_temp: float
    max_new_tokens: int = 50
    temperature: float = 0.7


class GenerateResponse(BaseModel):
    """텍스트 생성 응답 스키마"""
    generated_text: str
    prompt: str
    generation_time: float


class StopOnSequences(StoppingCriteria):
    """특정 문자열 시퀀스가 나오면 생성을 중지하는 클래스"""

    def __init__(self, stop_sequences: List[str], tokenizer, prompt_length: int):
        self.stop_sequences = stop_sequences
        self.tokenizer = tokenizer
        self.prompt_length = prompt_length

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        # 생성된 부분만 디코딩 (프롬프트 제외)
        generated_ids = input_ids[0][self.prompt_length:]
        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        # stop sequence 체크
        for stop_seq in self.stop_sequences:
            if stop_seq in generated_text:
                return True

        return False


def clean_generated_text(text: str) -> str:
    """
    생성된 텍스트에서 불필요한 형식을 제거하고 정제합니다.

    Args:
        text: 원본 생성 텍스트

    Returns:
        str: 정제된 텍스트
    """
    if not text:
        return text

    # 1. 마크다운 형식 제거 (---, ***, ##, 등)
    text = re.sub(r'^---+\s*', '', text, flags=re.MULTILINE)  # --- 제거
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** 제거
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # ### 헤더 제거

    # 2. 레이블 제거 ("출력:", "전광판 메시지:", "답:", 등)
    text = re.sub(r'^(출력|답변|답|메시지|전광판\s*메시지)\s*[:：]\s*', '', text, flags=re.IGNORECASE)

    # 3. 괄호와 그 안의 내용 제거 (예: "(또는)", "(예시)")
    text = re.sub(r'\([^)]+\)', '', text)

    # 4. 여러 문장이 있는 경우 첫 번째 완성된 문장만 추출
    # 한국어 문장 종결: ., !, ?, 요, 세요, 니다, 어요, 해요 등
    sentences = re.split(r'([.!?]|\s(?:요|세요|니다|어요|해요|습니다|ㅂ니다|예요|네요)(?:\s|$))', text)

    # 첫 번째 완성된 문장 찾기
    first_sentence = ""
    for i in range(0, len(sentences), 2):
        if i < len(sentences):
            sent = sentences[i].strip()
            # 종결어미가 있는지 확인
            if i + 1 < len(sentences):
                sent += sentences[i + 1]

            if sent and len(sent) > 10:  # 너무 짧은 문장은 제외
                first_sentence = sent
                break

    # 문장을 찾지 못한 경우 원본 사용
    if not first_sentence:
        first_sentence = text

    # 5. 앞뒤 공백 및 개행 정리
    first_sentence = first_sentence.strip()
    first_sentence = re.sub(r'\s+', ' ', first_sentence)  # 연속된 공백을 하나로

    # 6. 특수문자 정리 (이모지 등)
    # 한글, 영문, 숫자, 기본 문장부호만 허용
    first_sentence = re.sub(r'[^\w\s.!?°℃,\-~가-힣]', '', first_sentence)

    return first_sentence


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
        logger.info(f"✓ 베이스 모델 로드 완료! (소요 시간: {elapsed:.1f}초)")

        # 파인튜닝 어댑터 로드 (옵션)
        use_finetuned = os.getenv('USE_FINETUNED', 'false').lower() == 'true'
        adapter_path = os.getenv('ADAPTER_PATH', './finetuned_model')

        if use_finetuned and os.path.exists(adapter_path):
            logger.info(f"파인튜닝 어댑터 로드 중: {adapter_path}")
            adapter_start = time.time()

            model = PeftModel.from_pretrained(model, adapter_path)
            model.eval()

            adapter_elapsed = time.time() - adapter_start
            logger.info(f"✓ 파인튜닝 어댑터 로드 완료! (소요 시간: {adapter_elapsed:.1f}초)")
        elif use_finetuned:
            logger.warning(f"파인튜닝 어댑터 경로가 존재하지 않습니다: {adapter_path}")
            logger.warning("원본 모델을 사용합니다.")
        else:
            logger.info("원본 모델 사용 (파인튜닝 미적용)")

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
        prompt_length = inputs['input_ids'].shape[1]

        # Stop sequences 설정 (불필요한 출력 조기 종료)
        stop_sequences = [
            "\n\n",  # 두 번의 줄바꿈
            "입력:",  # 새로운 입력 패턴 시작
            "예시",  # 예시 시작
            "---",  # 마크다운 구분선
            "**",  # 마크다운 강조
            "(또는)",  # 대안 제시
            "왜냐하면",  # 설명 시작
            "어색합니다",  # 평가/비판 시작
            "문맥상",  # 설명 시작
        ]

        # StoppingCriteria 설정
        stopping_criteria = StoppingCriteriaList([
            StopOnSequences(stop_sequences, tokenizer, prompt_length)
        ])

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
                # stopping_criteria=stopping_criteria,
                early_stopping=True
            )

        # 디코딩
        full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # 프롬프트 제거
        generated_text = full_output[len(request.prompt):].strip()

        # 후처리: <|im_end|> 이후 부분 제거 (Chat 형식 정리)
        if '<|im_end|>' in generated_text:
            generated_text = generated_text.split('<|im_end|>')[0].strip()

        cleaned_text = generated_text

        generation_time = time.time() - start_time

        logger.info(f"✓ 생성 완료 (소요 시간: {generation_time:.2f}초)")
        logger.info(f"원본 길이: {len(generated_text)}, 정제 후 길이: {len(cleaned_text)}")

        return GenerateResponse(
            generated_text=cleaned_text,
            prompt=request.prompt,
            generation_time=generation_time
        )

    except Exception as e:
        logger.error(f"생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"생성 실패: {str(e)}")


@app.post("/generate/temperature", response_model=GenerateResponse)
async def generate_temperature_message(request: TemperatureComparisonRequest):
    """
    온도 비교 전광판 메시지 생성 엔드포인트
    자동으로 구조화된 프롬프트를 생성하여 모델에 전달합니다.
    """
    if not model_loaded:
        raise HTTPException(status_code=503, detail="모델이 아직 로드 중입니다.")

    try:
        # Chat 형식 프롬프트 생성 (파인튜닝 데이터와 동일 형식)
        # 파인튜닝된 모델을 사용하는 경우 이 형식이 최적
        use_chat_format = os.getenv('USE_CHAT_FORMAT', 'true').lower() == 'true'

        if use_chat_format:
            structured_prompt = PromptTemplates.get_temperature_chat_prompt(
                request.yesterday_temp,
                request.today_temp
            )
            logger.info(f"[Chat 형식] 온도 비교 메시지 생성: 어제 {request.yesterday_temp}도 → 오늘 {request.today_temp}도")
        else:
            # 레거시 Instruction 형식 (호환성 유지)
            comparison_data = {
                'yesterday_avg_temp': request.yesterday_temp,
                'today_avg_temp': request.today_temp,
                'temp_change': request.today_temp - request.yesterday_temp,
                'temp_change_direction': '상승' if request.today_temp > request.yesterday_temp else '하강'
            }
            structured_prompt = PromptTemplates.get_temperature_comparison_prompt(comparison_data)
            logger.info(f"[Instruction 형식] 온도 비교 메시지 생성: 어제 {request.yesterday_temp}도 → 오늘 {request.today_temp}도")

        # 내부 generate 함수 호출
        gen_request = GenerateRequest(
            prompt=structured_prompt,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature
        )

        return await generate_text(gen_request)

    except Exception as e:
        logger.error(f"온도 비교 메시지 생성 실패: {e}", exc_info=True)
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
