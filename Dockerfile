# Fly.io 배포용 Dockerfile
# Playwright + Python 환경

FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-unifont \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libglib2.0-0 \
    libnss3 \
    libxshmfence1 \
    libglu1 \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 브라우저 설치 (install-deps 제거, 수동 설치 완료)
RUN playwright install chromium

# 애플리케이션 코드 복사
COPY . .

# start.sh 실행 권한 부여
RUN chmod +x start.sh

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV CHROME_HEADLESS=true

# 포트 노출
EXPOSE 8000

# 시작 명령
CMD ["./start.sh"]
