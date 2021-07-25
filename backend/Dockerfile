FROM python:3.8.5
WORKDIR /code
COPY requirements.txt /code
RUN pip3 install -r requirements.txt
COPY . /code
RUN python manage.py migrate --noinput
RUN python manage.py createsuperuser
RUN python manage.py collectstatic --no-input
CMD gunicorn foodgram_project.wsgi:application --bind 0.0.0.0:8000