FROM python:3.12
RUN pip install --upgrade pip
COPY . .
RUN pip install --default-timeout=3600 -r .settings/requirements_full.txt

ENTRYPOINT ["python", "src/main.py"]
