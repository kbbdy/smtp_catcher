FROM python:3.5-alpine
EXPOSE 1025 8025 8026

ENV USERNAME catcher

WORKDIR /app/
ADD ./smtp_catcher /app/smtp_catcher
ADD ./requirements.txt requirements.txt


RUN pip --no-cache-dir install -r requirements.txt  \
 && rm -f /tmp/*

 #&& useradd -M --uid 1000 $USERNAME  \
 #&& chown $USERNAME /app
#
#RUN pip install --no-cache-dir -r requirements.txt

#USER $USERNAME

