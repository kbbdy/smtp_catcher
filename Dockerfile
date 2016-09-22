FROM python:3.5-alpine
EXPOSE 1025 8025 8026

ENV USERNAME catcher

WORKDIR /app/
ADD ./smtp_catcher /app/smtp_catcher
ADD ./requirements.txt requirements.txt
ADD ./entrypoint.py entrypoint.py


RUN pip --no-cache-dir install -r requirements.txt  \
 && rm -f /tmp/*

ENTRYPOINT ["python", "/app/entrypoint.py"]
CMD ["catcher"]

