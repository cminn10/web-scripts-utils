FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt  .

RUN pip install --no-cache-dir -r requirements.txt

COPY acrnm_monitor.py .

VOLUME /app/data

CMD ["python", "acrnm_monitor.py"]