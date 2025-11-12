FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data dir
RUN mkdir -p /app/data

EXPOSE 8050

CMD ["python", "src/app.py"]