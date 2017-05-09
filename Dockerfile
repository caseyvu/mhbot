FROM caseyvu/ubuntu_python_nodejs
MAINTAINER vuanhthu888@gmail.com
USER root

RUN echo postfix postfix/mailname string caseyvu.com | debconf-set-selections && \
    echo postfix postfix/main_mailer_type string 'Internet Site' | debconf-set-selections && \
    apt-get install -y postfix
ADD . /opt/mhbot
RUN apt-get install -y libfontconfig && \
    cd /opt/mhbot && pip3 install -r requirements.txt && npm -g install phantomjs-prebuilt

CMD /opt/mhbot/deploy/run