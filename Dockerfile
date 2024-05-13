FROM python:3.10-slim

ENV POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

CMD ["uvicorn", "test_service.main:app", "--log-config", "utils/uvicorn_config.ini", "--host", "0.0.0.0", "--port", "8000"]