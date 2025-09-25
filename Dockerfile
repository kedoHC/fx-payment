FROM python:3.11
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:80 app:app"]