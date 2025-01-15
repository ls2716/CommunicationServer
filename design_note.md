# Django Channels Communication Server

## 1. Overview

- Application Name: Django Channels Communication Server
- Purpose: Provide production-ready websocket communication server using Django
  Channels.
- Target Audience: Any internal application and potential external users who want to
  copy the project.

## 2. Goals

1. **Real-Time Communication**: Implement websocket communication for real-time
   updates. Any valid user should be able to create a secure websocket connection channel
   to communicate with other users which do not have to have a valid user account.

## 3. Functionalities

- Core Features: 
  - Create a communication channel given a valid user.
  - Send/receive messages in real-time.
- Optional Features: 

## 4. User Interface (UI) Design

- No necessary UI design is needed for this project.
- Thhe UI can use djangorestframework or base html templates.

## 5. Endpoints and Data Flow

- API Endpoints: 
  - create_communication_channel: POST request to create a communication channel.
  - delete_communication_channel: DELETE request to delete a communication channel.
- Websockets: 
  - ws://<host>/ws/communication_channel/<channel_id>/: Websocket connection to
    communicate with other users.
- Data Flow: Attach diagrams illustrating data interactions.

## 6. Tech Stack

- Front-End: None
- Back-End: Django Channels, Daphne, Redis, Nginx
- Database: sqlite3, Redis
- Additional Tools: Hosted on Contabo VPS

## 7. Logic and Architecture

- Architecture Diagram: ...
- Module Interactions: ...
- Error Handling and Security: ...

## 8. Challenges and Solutions

- Potential Challenges: Complexity of websocket communication.
- Mitigation Strategies: Use ChatGPT for explanations.
