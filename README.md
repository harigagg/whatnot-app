
# User Access Management Service

A simple service to manage user access based on event-driven rules.

## Project Structure

```text

whatnot-app/
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

    ```bash
    git clone git@github.com:harigagg/whatnot-app.git
    cd whatnot-app
    ```

2. Build and start the services:

   ```bash
   docker-compose up --build
   ```

2. The application will be accessible at: [http://localhost:5005](http://localhost:5005).

## Configuration

The application uses environment variables for configuration. Key settings include:

#### PostgreSQL:
```
POSTGRES_USER: Database username.
POSTGRES_PASSWORD: Database password.
POSTGRES_DB: Database name.
```

#### Redis:
```
REDIS_HOST: Hostname for Redis (default: redis).
REDIS_PORT: Port for Redis (default: 6379).
```

## Running Tests
To run tests it can be done outside and inside the docker container(I prefer to execute the test commands inside the application container as it will not disturb my local setup):

Note: Run the docker-compose command before running the below commands

1. Access the Flask app container:
    ```bash
    docker exec -it flask_app_container bash
    ```
2. Run tests:

    ```bash
    pytest
    ```
3. Run Locust: (For stress testing)
    ```bash
    locust -f locustfile.py
    ```

## Endpoints

- `**POST /event**:` Receives events.
- `**GET /canmessage**`: Checks if the user can send messages.
- `**GET /canpurchase**`: Checks if the user can make purchases.
