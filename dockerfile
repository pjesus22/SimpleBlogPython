# Stage 1: Build the application
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project --no-dev
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

# Stage 2: Run the application
FROM python:3.12-alpine AS runtime
RUN apk add --no-cache libpq libjpeg-turbo libffi sqlite
RUN addgroup -S app -g 1000 && adduser -S app -G app -u 1000
RUN mkdir -p /var/data /var/www/static /var/www/media \
    && chown -R app:app /var/data /var/www/static /var/www/media
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
USER app
ENV PATH="/app/.venv/bin:$PATH"
COPY --chown=app:app docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "simple_blog.wsgi:application", "-c", "gunicorn.conf.py"]
