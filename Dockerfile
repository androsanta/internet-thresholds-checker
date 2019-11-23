FROM python:3.7.4-alpine

RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev libxslt tzdata
ENV TZ Europe/Rome

WORKDIR /app

# Create a virtualenv
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "internet_checker.app:app"]