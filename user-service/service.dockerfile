FROM python:3.10-slim
RUN pip install psycopg2-binary requests jwt
WORKDIR /user-service
COPY . /user-service

EXPOSE 5001

# Maybe bad idea, but it works
CMD ["sh", "-c", "sleep 10 && python user-service/main.py"]
