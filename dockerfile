# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Define environment variables
ENV DJANGO_SETTINGS_MODULE=djecommerce.settings

# Collect static files
RUN python manage.py collectstatic --noinput

# Run the Django development server
CMD ["gunicorn", "djecommerce.wsgi:application", "--bind", "0.0.0.0:8000"]
