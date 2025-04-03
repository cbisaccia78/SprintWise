FROM python:3.11

WORKDIR /usr/local/app/

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
EXPOSE 5000

# set up an app user so the container doesn't run as the root user
RUN useradd app
USER app

ENV PYTHONPATH=/usr/local/app

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.app:app"]