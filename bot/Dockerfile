FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY bot/requirements.txt bot/requirements.txt
RUN pip install --no-cache-dir -r bot/requirements.txt
COPY bot/ bot/
COPY knowledge/i18n/ knowledge/i18n/
EXPOSE 8081
CMD ["python", "bot/main.py"]
