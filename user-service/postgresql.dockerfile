FROM postgres:latest

ENV POSTGRES_DB=users
ENV POSTGRES_USER=user_admin
ENV POSTGRES_PASSWORD=eighty9@doublet

VOLUME /var/lib/postgresql/data
EXPOSE 5432
