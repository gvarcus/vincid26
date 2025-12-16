FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio de logs y instance
RUN mkdir -p logs instance app/static/uploads

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "--timeout", "120", "run:app"]
