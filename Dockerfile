FROM python:3.11-slim

WORKDIR /app

# جلوگیری از مشکلات لایبرری‌ها
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# نصب dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# کپی کل پروژه
COPY . .

# مهم: استفاده از PORT داینامیک (Railway / Render / VPS)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
