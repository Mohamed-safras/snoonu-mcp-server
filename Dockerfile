FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY . .

RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV SNOONU_MCP_PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://localhost:' + os.environ.get('PORT', os.environ['SNOONU_MCP_PORT']) + '/health').read()"

CMD ["sh", "-c", "gunicorn src.server:app -k uvicorn.workers.UvicornWorker -w ${SNOONU_MCP_WORKERS:-4} -b 0.0.0.0:${PORT:-${SNOONU_MCP_PORT}} --access-logfile - --error-logfile -"]
