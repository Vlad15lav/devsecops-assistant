FROM postgres:16

# Устанавливаем расширение pgvector
RUN apt-get update && apt-get install -y postgresql-16-pgvector && rm -rf /var/lib/apt/lists/*

EXPOSE 5432