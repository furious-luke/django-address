FROM python:3.9-slim
LABEL maintainer="furious.luke@gmail.com"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8

RUN    apt-get -qq update \
    && apt-get -y install \
        bash \
        locales \
        git \
        build-essential \
        libssl-dev \
    && pip install poetry \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/Etc/UTC /etc/localtime \
    && locale-gen C.UTF-8 || true

ARG USER_ID
ARG GROUP_ID
RUN    addgroup --gid $GROUP_ID user || true \
    && useradd -M -u $USER_ID -g $GROUP_ID user || true \
    && usermod -d /code user || true

RUN mkdir -p /code
WORKDIR /code

COPY ./example_site/pyproject.toml ./example_site/poetry.lock /code/
RUN    poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY ./example_site /code/
COPY ./address /code/address
RUN chown -R user:user /code
USER user

EXPOSE 8000

CMD ./manage.py migrate && ./manage.py runserver 0.0.0.0:8000
