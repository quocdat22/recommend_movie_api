# --- Stage 1: Build stage ---
# Use a full Python image to install dependencies
FROM python:3.9-slim as builder

# Set the working directory
WORKDIR /app

# Install poetry for better dependency management
# RUN pip install poetry

# Copy dependency files
COPY requirements.txt ./

# Install dependencies
# Using a virtual environment within the builder stage
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final stage ---
# Use a smaller, non-root base image for the final application
FROM python:3.9-slim

# Set non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application source code
COPY ./src ./src
COPY ./configs ./configs

# Make the virtual environment's Python the default
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# The --host 0.0.0.0 is crucial to expose the service outside the container
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
