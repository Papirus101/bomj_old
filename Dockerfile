FROM python:3
COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD python bot.py