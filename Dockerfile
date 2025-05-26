FROM public.ecr.aws/docker/library/python:3.13-alpine

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install curl for healthcheck
RUN apk update && apk add --no-cache curl && \ 
    pip install --upgrade pip setuptools wheel

# Install Poetry and dependencies
RUN pip install poetry

# Faster build pip on alpine
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --without dev

# Expose the port the app runs on
EXPOSE 8000

CMD ["python", "manage.py", "runserver"]