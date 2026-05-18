FROM python:3.13-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app/src"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install locales
RUN apt-get update -y \
    && apt-get install -y locales \
    && sed -i '/^# pt_BR.UTF-8 UTF-8/s/^# //' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=pt_BR.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=pt_BR.UTF-8
ENV LC_ALL=pt_BR.UTF-8

# Copy dependency files
COPY pyproject.toml uv.lock README.md /app/

# Install dependencies using uv
RUN uv sync --frozen --no-install-project --no-dev

# Copy project source code
COPY src /app/src

# Create logs directory
RUN mkdir -p /app/logs

# Expose the application port
EXPOSE 8002

# Run the application
CMD ["uv", "run", "uvicorn", "main:appAPI", "--host", "0.0.0.0", "--port", "8002"]
