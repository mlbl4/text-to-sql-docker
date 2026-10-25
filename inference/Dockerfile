FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/opt/huggingface

WORKDIR /app

# 1) PyTorch (CPU build): the heaviest layer and the one that changes least
RUN pip install --no-cache-dir torch==2.14.1 \
    --index-url https://download.pytorch.org/whl/cpu

# 2) Other Python libraries: copy only the requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Bake the model weights into the image
RUN python -c "from huggingface_hub import snapshot_download; \
snapshot_download('Qwen/Qwen2.5-Coder-0.5B-Instruct')"

# From now on, never try to reach Hugging Face: use the baked-in weights
ENV HF_HUB_OFFLINE=1

# 4) Application code: changes most often, so it goes last
COPY model.py app.py ./

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]