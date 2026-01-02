# N-Link Analysis - Docker Image
# Multi-service container for API and visualization dashboards
#
# Build: docker build -t nlink-analysis .
# Run:   docker-compose up

FROM python:3.11-slim-bookworm

LABEL maintainer="mgmacleod"
LABEL description="N-Link Rule Analysis - Wikipedia Link Graph Explorer"
LABEL version="1.0.0"

# Prevent Python from writing bytecode and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY nlink_api/ ./nlink_api/
COPY n-link-analysis/ ./n-link-analysis/

# Set PYTHONPATH to include analysis scripts
ENV PYTHONPATH="/app:/app/n-link-analysis/scripts"

# Default environment variables for API
ENV DATA_SOURCE=local
ENV LOCAL_DATA_DIR=/app/data/wikipedia/processed
ENV ANALYSIS_OUTPUT_DIR=/app/data/wikipedia/processed/analysis
ENV MAX_WORKERS=4
ENV DEBUG=false
ENV API_PREFIX=/api/v1

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports for all services
# 8000 - N-Link API
# 8055 - Basin Geometry Viewer
# 8056 - Multiplex Analyzer
# 8060 - Tunneling Explorer
# 8070 - Reports Gallery
EXPOSE 8000 8055 8056 8060 8070

# Default command runs the API
ENTRYPOINT ["/entrypoint.sh"]
CMD ["api"]
