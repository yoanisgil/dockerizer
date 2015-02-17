FROM django:1.7.2-python2
MAINTAINER Yoanis Gil<gil.yoanis@gmail.com>

ADD ./jessie-contrib.list /etc/apt/sources.list.d/
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install nginx-full &&  rm -rf /var/lib/apt/lists/*

# Remove default site so it won't conflict with the Django app.
RUN rm -f /etc/nginx/sites-enabled/default

# Install required pythong packages.
RUN pip install supervisor gunicorn futures

# file management, everything after an ADD is uncached, so we do it as late as
# possible in the process.
RUN mkdir -p /webapp/deploy/run
RUN mkdir -p /webapp/deploy/dockerizer
ADD ./deploy.sh /webapp/deploy/deploy.sh
ADD ./run_pip.sh /webapp/deploy/run_pip.sh
ADD ./supervisord.conf /etc/supervisord.conf
ADD ./nginx.conf /etc/nginx/nginx.conf
ADD ./app /webapp/deploy
ADD ./dockerizer /webapp/deploy/dockerizer

RUN /webapp/deploy/run_pip.sh 

# restart nginx to load the config
RUN service nginx stop 
