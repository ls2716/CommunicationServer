# Work Log of the Communication Server Project

## 2025-09-01

- The project was created and its goals were defined.
- The web app was designed and the design was documented in the `design_note.md` file.
- Some of the design considerations are not included and have to be added to the design
  note.
- The server works in production but the production code is in disagreement with the
  development version - there is a need to join the two versions using conditional
  statements and configuration files.

### Models and decisions

The communication server works as follows:

- There are CustomUsers which represent certified apps. Each customer user has a
  username and api_key in addition to standard user fields which are not used.
- Given the api_key, the app can create communication rooms and endpoints to these rooms
  which can be then used/consumed by the users i.e. frontend clients.
- For every action endpoint (excluding 'main/' and 'admin/'), the request must contain
  the api_key in the header. If the api_key is not valid, the server will return 403
  Forbidden.
- Given the api_key, the view gets a user and performs the requested action. There are
  following actions:
  - create_room - ('main/create_room/room_name/) creates a room with a given name
    assigned to the user and returns the success message or a failure message if the
    room name already exists for the given user.
  - delete_room - ('main/delete_room/room_name/) deletes a room with a given name
    assigned to the user and returns the success message or a failure message if the
    room name does not exist for the given user.
  - list_rooms - ('main/list_rooms/) returns a list of rooms assigned to the user.
  - add_endpoint - ('main/add_endpoint/room_name/permission_type/) adds an endpoint to a
    given room with a given permission type (read_and_write or just read). The view
    returns the endpoint code which can be used to connect to the room.
  - delete_endpoint - ('main/delete_endpoint/room_name/endpoint_code/) deletes an
    endpoint with a given code from a given room.
  - list_endpoints - ('main/list_endpoints/room_name/) returns a list of endpoints
    assigned to a given room.

#### Future modification - what and why

The add endpoint url should allow for adding a meta information to the endpoint which
will then be attached to every message send by the endpoint. This will allow for
tracking the author of the message.

## 2025-10-01

### Deployment

The app is deployed on a remote server supplied by Contabo. The server is running Ubuntu
20 LTS. The app is deployed using nginx and daphne with additional SSL installed using
certbot.

Daphne is installed within the virtual environment and will be run as a service using
systemd. The service file will be located in the `communication_server.service` file.

The app is working due to some preliminary tests using ssh session run:

```bash
daphne -b 127.0.0.1 -p 8002 communication_server.asgi:application
```

The service has yet to be installed and tested.

That said, the nginx configuration is working and SSL works for both http and websocket
connections. As mentioned before, I need to join the production and development code to
make all work seamlessly.

### Project goals

The main goal of the project is a communication server which can be used by other
projects to create communication rooms and endpoints.

The project will be part of the portfolio and should be commented enough so that it can
be understood and used by other developers.

The project should be deployed on a remote server and should be working in production
mode. There should be a link to a demo which exposes an account as well as running rooms
and endpoints.

## 13.01.2025

### wss vs ws

I modified the js code to check which protocol to use. The code is as follows:

```javascript
const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";

const chatSocket = new WebSocket(
  ws_scheme + window.location.host + "/ws/endpoint/" + endpointCode + "/"
);
```

The code checks if the protocol is https and if so, uses wss, otherwise uses ws. This
should work in all cases.

### Deployment

I have created a systemd service file for the daphne server. The service is running and
the server is working. The service file is located in the `daphne_communication_server.service`.

Contents of the file are as follows:

```bash
[Unit]
Description=Daphne Server for Communication Server
After=network.target

[Service]
User=lukasz
Group=lukasz
WorkingDirectory=/home/lukasz/communication_server/channels_server
ExecStart=/home/lukasz/communication_server/venv/bin/daphne -b 127.0.0.1 -p 8002 channels_server.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

The nginx configuration is working and the app is running on the remote server. The
configuration is as follows:

```nginx
server {
    server_name comms.ls314.com;

    # Static files
    location /static/ {
        alias /home/lukasz/communication_server/channels_server/static/;
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
        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/comms.ls314.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/comms.ls314.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}
server {
    if ($host = comms.ls314.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;
    server_name comms.ls314.com;
    return 404; # managed by Certbot
}
```

For base implementation of nginx server, one should start with http version of the
configuration and then add the https version using certbot which will add the necessary
configuration for the SSL. (For the base configuration, just exclude all ssl related
lines and modify to listen on 80).

### Next steps

Implement the previously mentioned meta information for the endpoint.
Make a demo and advertise the project.
Add redis, deployment configuration and automatic deployment.

## 14.01.2025

### Added loading config from parent directory

For remote server deployment, an appropiate configuration file should be loaded from the
parent directory which is the same one that contains venv and is thus machine-specific.

### CORS policy

Modified the CORS policy so that websockets can be used from any origin. The policy is
enforced on nginx level and in Django settings. The remote version does not include correct
CORS policy but works since now it copies from ALLOWED_HOSTS which is ['*'].

After the copy, the cors policy would still work.

In asgi.py, the following code was added:

```python
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import  OriginValidator

from django.core.asgi import get_asgi_application

from main.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'channels_server.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()



application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": OriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
            allowed_origins=['*'],
        ),
    }
)
```

In nginx configuration, the following lines were added:

```nginx
# WebSocket handling
    location /ws/ {
        # BLOCK BELOW ADDED
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
        add_header 'Access-Control-Allow-Origin' '*' always; # ADDED
        add_header 'Access-Control-Allow-Credentials' 'true' always; # ADDED
    }
```

## 15.01.2025

Initialised repo and put online.

Added redis to the project following chatgpt instructions.

### Goals

- Finish README.md
- Advertise demo + mention availability of api-key for developers
- Write a blog post
- Update ls314.com with the project.
- Add endpoint meta information for author tracking.
- Add message timestamp
