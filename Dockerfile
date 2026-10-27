# python + jupyter for the garage door notebooks
# packages come from uv.lock, so everyone gets the same versions

FROM python:3.13.13-slim

# uv, pinned to the version that made uv.lock
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /bin/uv

# keep the environment outside /app, so it doesn't clash with a .venv on your mac
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# install exactly what's in the lock file. --frozen fails if the lock is out of date
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project

EXPOSE 8888

# jupyter with no password. only safe because compose publishes it on 127.0.0.1 (this computer only)
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", \
     "--IdentityProvider.token=", "--ServerApp.root_dir=/app"]
