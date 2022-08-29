FROM python:3.9 
ADD main.py .
RUN pip install requests schedule
CMD ["python", "-u", "./main.py"] 