# Defines the blueprint for the container image. Installs dependencies,
# sets up a secure non-root user, and specifies the startup command to run the 
# agent web server.

# Use an official lightweight Python image as the base
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Create a non-root user for security best practices
RUN adduser --disabled-password --gecos "" myuser

# Copy and install dependencies first to leverage Docker's layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code into the container
COPY . .

# Change ownership of EVERYTHING in /app to the non-root user
# Without this, the running agent would be denied permission to write files.
RUN chown -R myuser:myuser /app

# Switch the active user from root to the non-root user
USER myuser

# Add the user's local binary directory to the system's PATH
ENV PATH="/home/myuser/.local/bin:$PATH"

# Define the command to run when the container starts
# CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
# CMD ["adk", "api_server", "--a2a", "--host", "0.0.0.0", "--port", "8080", "wiki_researcher"]
# Start the remote agent using uvicorn
CMD ["uvicorn", "wiki_researcher.agent:a2a_app", "--host", "0.0.0.0", "--port", "8080"]

