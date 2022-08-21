FROM postgres
EXPOSE 5432
COPY db/init.sql /docker-entrypoint-initdb.d