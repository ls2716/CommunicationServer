# Django Channels Communication Server

The purpose of this project is to create a production-ready websocket communication
server using Django Channels. The server should be able to serve any other application
that needs real-time communication.

## Overview

The main functionality of the server is provision of secure websocket connections to
applications and thus provide real-time communication between clients.

Every app that requires real-time communication is provided with an api-key. Given the
api-key, the app can provide create communication rooms and add endpoints to the rooms
which can be then utilised by the frontend clients.

## Installation for development

1. Clone the repository
2. In the main repository directory create a virtual environment

```bash
python -m venv venv --upgrade-deps
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

6. Change the directory to the channels_server folder

```bash
cd channels_server
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
api-key - this means you don't have to modify the headers to use the app but it is a
security risk. Change the api-key in the admin panel in production.

9.  Run the server

```bash
python manage.py runserver
```

10. (optional) Run the demo setup to test the app

```bash
python setup_demo.py
```

This will provide you with links to chat rooms with two separate endpoints.

## Usage - api-keys, rooms, endpoints

The usage for a given application is as follows:

1. Provision a new api-key for the application in the admin panel. For that purpose
   create a new user and then create a new api-key for that user. The api-key is a
   string that is used to authenticate the user and the application. Make sure that the
   api-key is long (ideally >80 characters) and random enough to prevent brute-force
   attacks.
2. Given the api-key, the app authenticates itself by sending the api-key in the headers
   of the request. The header should be `API-KEY: <api-key>`.
3. The app can create a new room by sending a GET request to the `/create-room/`
   endpoint like so:

```
<host>/create-room/<room_name>/
```

The room name should be unique for the given api-key. The room name should be
alphanumeric and can contain dashes and underscores. If the room exists, the server will
return the 404 status code.

Room can be deleted by sending a GET request to the `/delete-room/` endpoint like so:

```
<host>/delete-room/<room_name>/
```

4. App can create endpoints in the room by sending a POST request to the
   `/add_endpoint/` endpoint like so:

```
<host>/add_endpoint/<room_name>/<permissions>/?identity=<identity>
```

If the room does not exist, the server will return the 404 status code. The permissions
has to be one of the following:

- 'read' - the endpoint will receive the messages from the room but anything sent to the
  endpoint will be ignored
- 'write' - the endpoint can send messages to the room but will not receive any messages
- 'readwrite' - the endpoint can send and wil receive messages from the room

For example, in a chat application, the endpoints should have the 'readwrite'
permissions. But, in an application like chatgpt, the llm should only send messages to
the room while the frontend should only receive messages and not be able to send
anything.

The identity is a string that is used to identify the endpoint. The identity can be
anything and it can be used by frontend to identify the endpoint. If no identity is
provided, the identity will be "Anonymous".

The add_endpoint endpoint will return a json with the following structure:

```json
{
  "code": "<endpoint_code>",
  "room": "<room_name>",
  "permissions": "<permissions>",
  "identity": "<identity>"
}
```

The endpoint code is a string that is used to authenticate the endpoint.

5. The endpoint can be deleted by sending a GET request to the `/delete_endpoint/`
   endpoint like so:

```
<host>/delete_endpoint/<room_name>/<endpoint_code>/
```

6. Additionally, you can list the rooms and endpoints for the room by using following
   endpoints:

```
<host>/list_rooms/
```

This will return a json with the following structure:

```json
{
  "rooms": ["<room_name_1>", "<room_name_2>", ...]
}
```

```
<host>/list_endpoints/<room_name>/
```

This will return a json with the following structure:

```json
{
  "endpoints": [
    {
      "code": "<endpoint_code_1>",
      "permissions": "<permissions_1>",
      "identity": "<identity_1>"
    },
    {
      "code": "<endpoint_code_2>",
      "permissions": "<permissions_2>",
      "identity": "<identity_2>"
    },
    ...
  ]
}
```

### Usage - sending and receiving messages

Given the endpoint code, the app can establish websocket connections. The websocket
connections should be established with the following url:

```
ws://<host>/ws/endpoint/<endpoint_code>/
```

(in production, one will use wss instead of ws)

The websocket connection will be used to send and receive messages. The messages should
be in the following format:

```json
{
  "message": ...
}
```

The message can be anything that can be serialised to json. The server will broadcast
the message to all the endpoints in the room that have the 'read' or 'readwrite'
permissions.

## Production-ready deployment with daphne, nginx, certbot and redis

The deployment processes assumes following:

- Server running Ubuntu >=20.04 with sudo access and exposed ports 80 and 443
- Domain name with A record pointing to the server
- Python >=3.8 installed on the server with virtualenv
- nginx installed on the server and running
- Redis installed on the server and running on localhost with port 6379 (default
  settings)
- installed certbot

1. Repeat steps 1-8 from the installation process on the remote server
2. Modify the config.yaml.

```yaml
# config.yaml
SECRET_KEY: "your_secret_key"
DEBUG: False
ALLOWED_HOSTS: ['<domain_name>']
CSRF_TRUSTED_ORIGINS: ['https://<domain_name>']
USE_REDIS: True
```

3. Create a systemd service for the daphne server

```bash
sudo nano /etc/systemd/system/daphne.service
```

and configure daphne.service like so:

```
[Unit]
Description=Daphne Server for Communication Server
After=network.target

[Service]
User=user
Group=user
WorkingDirectory=/home/user/path/to/dir/channels_server
ExecStart=/home/user/path/to/dir/venv/bin/daphne -b 127.0.0.1 -p 8002 channels_server.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Remember to update the User, Group, WorkingDirectory, ExecStart accordingly.

1. Enable and start the daphne service

```bash
sudo systemctl enable daphne
sudo systemctl start daphne
```

5. Create a VirtualHost configuration for nginx

```bash
sudo nano /etc/nginx/sites-available/channels_server
```

and configure the VirtualHost like so:

```
server {
    server_name <domain_name>;

    # Static files
    location /static/ {
        alias /home/user/path/to/dir/channels_server/static/;
    }

    # Proxy HTTP requests to Daphne/Uvicorn
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket handling
    location /ws/ {
         if ($request_method = OPTIONS) {
                add_header 'Access-Control-Allow-Origin' '*';
                add_header 'Access-Control-Allow-Credentials' 'true';
                add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
                return 204;
        }

        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Allow CORS for WebSocket connections
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
    }

    listen 80;

}

Remember to update the server_name and the static files path.

6. Enable the VirtualHost

```bash
sudo ln -s /etc/nginx/sites-available/channels_server /etc/nginx/sites-enabled/
```

7. Test the nginx configuration

```bash
sudo nginx -t
```

8. Add SSL certificate with certbot.

```bash
sudo certbot --nginx
```

Follow the prompts to add the SSL certificate to the domain name.

9. Restart nginx

```bash
sudo systemctl restart nginx
```

10.  The server should be running on the domain name. 
