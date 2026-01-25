# Use a slim Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir requests

# Copy the script
COPY discussion_sys.py .

# Environment variables (can be overridden at runtime)
ENV LMSTUDIO_API_URL="http://host.docker.internal:1234/v1/chat/completions"
ENV NUM_AGENTS=3
ENV NUM_ROUNDS=2

# Run the script
CMD ["python", "discussion_sys.py"]
