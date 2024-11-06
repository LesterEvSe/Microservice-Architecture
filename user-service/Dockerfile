FROM python:3.10-slim
RUN pip install psycopg2-binary requests pyjwt
WORKDIR /user-service
COPY . /user-service

EXPOSE 5001
CMD ["python", "main.py"]
