# Official Python runtime as a parent image
FROM python:3.11

# Set working directory of repo in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Change directory to run crs_main.py
WORKDIR /app/crs_scraper

# Run the application
CMD ["python", "crs_main.py"]