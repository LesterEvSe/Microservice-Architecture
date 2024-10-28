FROM python:3.10-slim
RUN pip install psycopg2-binary
WORKDIR /task-service
COPY . /task-service

EXPOSE 5002

# Maybe bad idea, but it works
CMD ["sh", "-c", "sleep 10 && python task-service/main.py"]
