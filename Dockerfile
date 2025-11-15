FROM zcr.cloudzcp.net/cloudzcp/axmp-ai-agent-base:0.9.0

# install application
# ------------------------------------------------------------------------------
WORKDIR /application

RUN mkdir -p /application/files

RUN python -m venv /application/.venv && \
    /application/.venv/bin/pip install --upgrade pip setuptools && \
    /application/.venv/bin/pip install uv

COPY . .

RUN /application/.venv/bin/uv sync --no-cache --no-dev

# Check the content of the image
RUN ls -al .
# RUN tree ./application

EXPOSE 8000

CMD ["/application/.venv/bin/python", "src/movie_catalog_backend/__init__.py"]
