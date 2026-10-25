FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/opt/huggingface

WORKDIR /app

# 1) PyTorch (CPU build): the heaviest library, changes least
RUN pip install --no-cache-dir torch==2.14.1 \
    --index-url https://download.pytorch.org/whl/cpu

# 2) Only the tool needed to download the model
RUN pip install --no-cache-dir huggingface_hub==2.3.0
# 3) Model weights: depend only on the model, NOT on requirements.txt,
#    so changing a library no longer re-downloads the 988 MB
RUN python -c "from huggingface_hub import snapshot_download; \
snapshot_download('Qwen/Qwen2.5-Coder-0.5B-Instruct')"
ENV HF_HUB_OFFLINE=1

# 4) Other Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Application code: changes most often, so it goes last
COPY model.py app.py ./

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]