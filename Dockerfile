FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the full project into the image (keeps caching for requirements above)
COPY . /code

# Start the app by importing the package module so relative imports work
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
