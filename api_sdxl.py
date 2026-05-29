#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 SDXL IMAGE GENERATOR API — برای ربات VIP PLATINUM
اجرا: uvicorn api_sdxl:app --host 0.0.0.0 --port 8000
"""

import io
import torch
from fastapi import FastAPI, Form, Response
from fastapi.responses import JSONResponse
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SDXL_API")

app = FastAPI()

# تنظیمات
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

logger.info(f"🚀 Loading SDXL on {DEVICE}...")

# بارگذاری مدل (یک بار در هنگام استارت)
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=DTYPE,
    use_safetensors=True,
    variant="fp16" if DEVICE == "cuda" else None
)

pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
pipe = pipe.to(DEVICE)

# بهینه‌سازی برای GPU
if DEVICE == "cuda":
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()
    pipe.enable_model_cpu_offload()

logger.info(f"✅ SDXL Ready on {DEVICE}")

@app.post("/generate/")
async def generate_image(
    prompt: str = Form(...),
    negative_prompt: str = Form("worst quality, low quality, blurry, deformed, ugly, bad anatomy"),
    width: int = Form(1024),
    height: int = Form(1024),
    steps: int = Form(30),
    guidance_scale: float = Form(7.5)
):
    try:
        logger.info(f"🎨 Generating: {prompt[:100]}...")
        
        # ترکیب پرامپت با سبک کریپتو
        full_prompt = f"{prompt}, cryptocurrency theme, blockchain background, futuristic, high quality, 4K, detailed, professional"
        
        result = pipe(
            prompt=full_prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
        )
        
        image = result.images[0]
        
        # تبدیل به JPEG
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=85)
        buf.seek(0)
        
        logger.info("✅ Image generated successfully")
        return Response(content=buf.getvalue(), media_type="image/jpeg")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/health")
async def health():
    return {"status": "ok", "device": DEVICE, "model": "SDXL-Base-1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
