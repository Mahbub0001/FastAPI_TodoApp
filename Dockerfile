FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# The repository requirements file is UTF-16 encoded; pip expects UTF-8.
RUN python -c "from pathlib import Path; p = Path('requirements.txt'); p.write_text(p.read_text(encoding='utf-16'), encoding='utf-8')" \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]