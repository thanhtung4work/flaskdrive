# Flask  Drive Clone

This project is a **Google Drive clone** built with **Flask**, featuring file upload and user authentication. It also includes an AI service for **text summarization** as well as **monitoring** with **Prometheus** and **data storage** with **Minio**.

## Project Architecture

The project is structured using a **microservices architecture**, with three primary containers:

1. **Flask App**: Handles the frontend and backend logic, including file uploads, user management, and serving the main interface.
2. **AI Service**: A separate container responsible for text summarization. This service exposes an API that the Flask app interacts with.
3. **Monitoring (Prometheus)**: Monitors system performance and health metrics.

### Container Breakdown:

- **Flask App**:
  - **Frontend**: HTML/CSS/JS (using Bulma.css).
  - **Backend**: Flask handles routes, user authentication, and file management.
  - **Storage**: Each user has their own directory for storing text-based files (`.pdf` for now).
  
- **AI Service**:
  - Flask app interacts with this API to perform summarization tasks.
  
- **Prometheus**:
  - **Prometheus** collects metrics from the system.

- **Object storage**:
  - **Minio** stores data

## Features

- User authentication (Sign up, Log in, Log out).
- Each user has their own private directory for text-based files.
- **Text-based file upload only** (`.pdf` for now).
- AI-powered **text summarization** via a dedicated API.
- Real-time monitoring using **Prometheus**.

## Prerequisites

- Docker and Docker Compose installed on your machine.

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/thanhtung4work/flaskdrive
   cd flaskdrive
   ```

2. Install requirement modules:
    ```bash
    pip install -r requirements.txt
    ```

3. flask --app server init-db

4. Host flask app
    ```
    flask --app server run --host 0.0.0.0 --port 19009
    ```
5. Docker    
    ```
    docker compose up -d
    ```