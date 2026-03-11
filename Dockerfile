# Usamos una imagen ligera de Python
FROM python:3.12-slim

# Directorio de trabajo
WORKDIR /app

# Copiamos archivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Exponemos el puerto de Flask
EXPOSE 5000

# Comando para iniciar
CMD ["python", "app.py"]