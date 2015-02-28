*Introduction*

Dockerizer is django application aiming to help building Docker images and to launch docker containers.
This application assumes Docker is already installed and fully operational. If you have not please check
Docker's online documentation to see how to get started: https://docs.docker.com/installation/mac/#container-port-redirection


*Installation*

Please follow the installation steps bellow to get the project up and running:

* Clone the repository: https://github.com/yoanisgil/dockerizer.git 
* Install requirements: pip install -r requirements.txt
* Add your dockers settings to manager/settings.py:
    DOCKER_HOST = 'https://IP:PORT'
    DOCKER_TLS_VERIFY = 1
    DOCKER_CERT_PATH = '/PATH/TO/YOUR/DOCKER/CERTIFICATE'
    DOCKER_TLS_VERIFY = True 
* Install a celery broker: http://celery.readthedocs.org/en/latest/getting-started/brokers/index.html
* Launch celery: celery -A manager worker -l debug
* Launch the application: python manage.py runserver

*Usage*

You can now start building your dockers by visiting http://localhost:8000

