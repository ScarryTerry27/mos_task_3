FROM python:3.11-slim

WORKDIR /backend

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /backend

ENV PYTHONPATH=/backend
