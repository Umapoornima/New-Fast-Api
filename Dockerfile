# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install --no-root && \
    poetry add azure-storage-blob python-multipart anthropic jinja2

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run the FastAPI app
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
