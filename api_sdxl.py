import io
import torch
from fastapi import FastAPI, Form, Response
from fastapi.responses import JSONResponse
from diffusers import StableDiffusionXLPipeline
from contextlib import asynccontextmanager

# --- این بخش، مدل رو فقط 1 بار لود می کنه ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Loading SDXL Model...")
    app.pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True
    )
    # چرتکه رو میندازیم روی GPU که سریعتر کار کنه
    app.pipe = app.pipe.to("cuda")
    app.pipe.enable_attention_slicing() # برای مدیریت بهتر حافظه
    print("✅ Model is ready!")
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/generate/")
async def generate(prompt: str = Form(...)):
    try:
        # اون کلمه magic رو به پرامپت اضافه می کنیم
        final_prompt = f"crypto art, blockchain, futuristic, {prompt}"
        result = app.pipe(final_prompt, num_inference_steps=30).images[0]

        buf = io.BytesIO()
        result.save(buf, format="JPEG")
        buf.seek(0)
        return Response(content=buf.getvalue(), media_type="image/jpeg")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
