FROM python:3.11-slim

LABEL org.opencontainers.image.title="ToxiGuard NORA EarlyTox" \
      org.opencontainers.image.version="0.4.0" \
      org.opencontainers.image.licenses="Proprietary"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NORA_DATA_DIR=/app/.nora_data

RUN addgroup --system nora && adduser --system --ingroup nora nora
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY --chown=nora:nora . .
RUN mkdir -p /app/.nora_data && chown -R nora:nora /app/.nora_data
USER nora
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=3)" || exit 1
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
