# Start with a Python image.
FROM ubuntu:16.04

# Some stuff that everyone has been copy-pasting
# since the dawn of time.
ENV PYTHONUNBUFFERED 1

# Install some necessary things.
RUN apt-get update
RUN apt-get install -y python-dev wget

# Copy all our files into the image.
RUN mkdir /simple_python_api
WORKDIR /simple_python_api
COPY . /simple_python_api/

RUN wget http://peak.telecommunity.com/dist/ez_setup.py
RUN python ez_setup.py
RUN easy_install pip

# Install our requirements.
RUN pip install -U pip
RUN pip install -Ur requirements.txt

ENV DJANGO_VERSION 1.10.5

RUN pip install django=="$DJANGO_VERSION" djangorestframework

# Port to expose
EXPOSE 8000

# Collect our static media.
# RUN /simple_python_api/manage.py collectstatic --noinput

RUN /simple_python_api/manage.py makemigrations
RUN /simple_python_api/manage.py migrate

RUN echo "from apis.models import CustomUser; CustomUser.objects.filter(email='admin@admin.com').delete(); CustomUser.objects.create_superuser('admin@admin.com', 'admin', nick='admin')" | python manage.py shell

# Specify the command to run when the image is run.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]