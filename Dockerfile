FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY parse_nginx_log.py ./

ENTRYPOINT [ "python", "./parse_nginx_log.py" ]