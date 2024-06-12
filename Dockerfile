###
# build compiled wheels
FROM python:3.12 as build

WORKDIR /

# setup poetry
RUN pip install --no-cache-dir poetry

COPY pyproject.toml .
RUN poetry export --format requirements.txt --without-hashes --output requirements.txt
RUN pip wheel --wheel-dir /wheels-base --requirement requirements.txt --debug --verbose


###
# final image
FROM python:3.12 as final

# copy python dependency wheels from build stage
COPY --from=build /wheels-base/  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

WORKDIR /app
COPY . .

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
