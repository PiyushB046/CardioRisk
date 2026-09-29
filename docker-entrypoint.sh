#!/bin/sh
set -e
# Always (re)load data into Postgres; train only if no model is baked into the image.
if [ ! -f models/model.joblib ]; then
  python -m src.heart.train
else
  python -c "from src.heart.db import init_db; from src.heart import data; init_db(); data.run()"
fi
exec uvicorn api.main:app --host 0.0.0.0 --port 8000
