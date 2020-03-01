FROM mysql:8


ENV MYSQL_DATABASE umatter
ENV MYSQL_ROOT_PASSWORD root

RUN chown -R mysql:mysql /docker-entrypoint-initdb.d
ADD init.sql /docker-entrypoint-initdb.d/