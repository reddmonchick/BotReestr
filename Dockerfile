FROM python:3.11.5-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /src
COPY requirements.txt .
RUN pip install --no-cache -r requirements.txt
COPY . /src/
CMD ["python", "-m", "src"]