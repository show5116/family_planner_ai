# Use the official uv image based on Debian Bookworm slim and Python 3.13
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set the working directory
WORKDIR /app

# Copy dependency files first to maximize Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# --no-dev: Skip development dependencies
# --system: Install directly to the system Python, bypassing virtual environments
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application code
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev

# Ensure the app starts up without prompts (Railway handles environment variables magically, but we enforce Uvicorn settings)
ENV HOST=0.0.0.0
ENV PORT=8000

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI application using uvicorn correctly within the uv environment
CMD uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
