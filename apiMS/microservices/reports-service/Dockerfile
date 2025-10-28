FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY ../requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8006

# Comando de inicio
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]

