FROM python:3.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY api ./api
COPY web ./web
COPY models ./models
COPY data/raw ./data/raw
COPY docker-entrypoint.sh .
EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
