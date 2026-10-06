FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl nodejs libatomic1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY prisma prisma/
RUN prisma generate

COPY app app/
COPY start.sh .
RUN chmod +x start.sh

ENV PORT=8080
EXPOSE 8080

CMD ["./start.sh"]
