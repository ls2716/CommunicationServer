# Django Channels Communication Server

The purpose of this project is to create a production-ready websocket communication
server using Django Channels. The server should be able to serve any other application
that needs real-time communication.

## Overview

(What is the functionality of the server?)

### Demo endpoints

## Installation for development

1. Clone the repository
2. In the main repository directory create a virtual environment

```bash
python -m venv venv
```

(or equivalent command for your OS and python version)

3. Activate the virtual environment
4. Install the requirements from the requirements.txt file

```bash
pip install -r requirements.txt
```

5. Create a configuration file config.yaml in the main repository directory (the parent
   of channels_server folder)

```yaml
# config.yaml
SECRET_KEY: "your_secret_key"
DEBUG: True
ALLOWED_HOSTS: ["*"]
USE_REDIS: False
```

To generate a secret key you can use the following command:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

6. Collect the static files

```bash
python manage.py collectstatic
```

7. Make and apply the migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

8. Create a superuser

```bash
python manage.py createsuperuser
```

Then follow the prompts to create a superuser. This will create a user with an empty
api-key - this means you don't have to modify the headers to use the app but it is
a security risk. Change the api-key in the admin panel in production.

9.  Run the server

```bash
python manage.py runserver
```

10. (optional) Run the demo setup to test the app

```bash
python setup_demo.py
```

This will provide you with links to chat rooms with two separate endpoints.



## Usage - api_tokens, rooms, endpoints

... (explain the usage)

## Production-ready deployment with daphne, nginx, certbot and redis

... (explain the deployment process)
