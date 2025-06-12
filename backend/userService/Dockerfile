# Use a full Python image instead of slim
FROM python:3.13

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
# Added non-interactive frontend to avoid prompts during build
# Added LaTeX packages for PDF generation
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-extra-utils \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a directory for generated PDFs
RUN mkdir -p /app/generated_pdfs

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the FastAPI app with auto-reload for development
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]