FROM python:3.7

WORKDIR /book_hub

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY Pipfile Pipfile.lock /book_hub/

RUN pip install pipenv && pipenv install --system --ignore-pipfile

COPY . /book_hub/