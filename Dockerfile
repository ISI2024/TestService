FROM python:3.10-alpine3.16
WORKDIR /web
COPY requirements.txt /web/requirements.txt
RUN pip3 install --no-cache-dir -r /web/requirements.txt
COPY  .  /web/
CMD ["uvicorn", "rest_api.main:app", "--log-config", "utils/uvicorn_config.ini", "--host", "0.0.0.0", "--port", "8000"]