FROM python:3.12

WORKDIR /

COPY release_helper release_helper/

# setup python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh .

ENTRYPOINT ["/entrypoint.sh"]
