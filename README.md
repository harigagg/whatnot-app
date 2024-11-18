
# User Access Management Service

A simple service to manage user access based on event-driven rules.

## Project Structure

```text

user_access_service/
├── app.py                  # Main entry point of the application
├── config.py               # Configuration settings
├── models/
│   ├── __init__.py         # Initializes SQLAlchemy and Redis connections
│   ├── user_state.py       # UserState model and database functions
│   ├── credit_card.py      # CreditCard model and database functions
├── services/
│   ├── __init__.py
│   ├── access_control.py   # Business logic for access control rules
│   ├── tripwire.py         # Tripwire management and monitoring
├── routes/
│   ├── __init__.py
│   ├── event_handler.py    # Routes to handle event POST requests
│   ├── access_checker.py   # Routes to check user access (GET requests)
├── tests/
│   ├── __init__.py
│   ├── test_event_handler.py  # Unit tests for event handling
│   ├── test_access_checker.py # Unit tests for access checking
│   ├── test_access_control.py # Unit tests for access controling
│   ├── test_add_credit_card.py # Unit tests for adding credit cards
│   ├── test_tripwire.py       # Unit tests for tripwire functionality
├── Dockerfile             # Dockerfile for Flask app
├── .env.dev               # environment file for local dev
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Features

* Flask Framework: Core web application functionality.
* PostgreSQL: Relational database for storing application data.
* Redis: In-memory data store for caching and real-time data management.
* Dockerized: Fully containerized using Docker for easy deployment.
* Gunicorn: Production-ready WSGI HTTP server for serving the Flask app.

## Setup and Installation

1. Clone the Repository
```
git clone git@github.com:harigagg/whatnot-app.git
cd <repository-folder>
```

1. Build and start the services:

   ```bash
   docker-compose up --build
   ```

2. Access `user_access_service` at [http://localhost:5000](http://localhost:5000).

3. Modify `event_sender/send_events.py` to customize event data as needed.

    - This is for testing purposes only and to demonstrates and example of an external service sending events.  Feel free to modify in any way you choose.

4. Implement your code in `app.py`
    - Note: `app.py` is just the entrypoint.  Feel free to break of the code into multiple files as you see fit.

## Endpoints

- `**POST /event**:` Receives events.
- `**GET /canmessage**`: Checks if the user can send messages.
- `**GET /canpurchase**`: Checks if the user can make purchases.

