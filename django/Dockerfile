 # Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory contents into the container at /usr/src/app
COPY . .

# Set the environment variable to tell Django to run in production mode
ENV DJANGO_SETTINGS_MODULE=django_project.settings

# Expose the port the app runs on
EXPOSE 8000

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "django_project.wsgi:application"]
