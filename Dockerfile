FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached when only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY wsgi.py .

# Run as a non-root user; uid 1000 matches the default user on most Linux
# hosts, so the bind-mounted logs/ folder stays writable
RUN useradd --uid 1000 --create-home appuser && mkdir logs && chown appuser logs
USER appuser

EXPOSE 5000

# One worker so only one process writes and rotates logs/app.log
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--preload", "wsgi:app"]
