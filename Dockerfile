FROM python:3.11-alpine
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apk add --no-cache --virtual .build-deps python3-dev make gcc g++ libc-dev && \
    pip3 install --no-cache-dir --upgrade -r requirements.txt && \
    apk del .build-deps
EXPOSE 8000
COPY main.py main.py
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
