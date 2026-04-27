FROM postgres:16-alpine

# Copiar el script de inicialización directamente en la imagen
# PostgreSQL ejecuta automáticamente todo lo que esté en /docker-entrypoint-initdb.d/
COPY init.sql /docker-entrypoint-initdb.d/init.sql
