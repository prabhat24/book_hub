FROM python:3.7

WORKDIR /book_hub

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /book_hub/

RUN pip install -r requirements.txt

COPY . /book_hub/