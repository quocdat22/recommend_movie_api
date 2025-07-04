# Movie Recommendation API

This is a FastAPI-based API for serving movie recommendations. It uses a Sentence Transformer model for text-based recommendations and leverages a Supabase backend with `pgvector` for similarity search.

This service is part of a larger MLOps project. See the main project [README](../README.md) for the overall architecture.

## ✨ Features

- **Two Recommendation Modes**:
  - `/api/v1/recommendations/by-title`: Get recommendations for movies similar to a given title.
  - `/api/v1/recommendations/by-text`: Get recommendations based on a free-text query (e.g., "a movie about dreams").
- **FastAPI**: High-performance, easy-to-use Python web framework.
- **Pydantic**: Robust data validation for API requests and responses.
- **Dockerized**: Comes with a multi-stage `Dockerfile` for building a small, efficient, and secure production image.
- **Dependency Injection**: The recommendation model is loaded only once at startup for maximum performance.
- **Configurable**: Settings are managed via a `.env` file and a `configs/` directory.
- **Comprehensive Monitoring**: Built-in Prometheus metrics for performance tracking, with Grafana dashboards for visualization.

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.
- A Supabase project with the database schema and RPC functions (`match_movies`, `match_movies_by_text_embedding`) already set up.

### 1. Configuration

Create a `.env` file in the root of the `movie-serving-api` directory by copying the example:

```bash
cp .env.example .env
```

Now, open the `.env` file and fill in your Supabase credentials:

```env
# .env
SUPABASE_URL="https://your-project-ref.supabase.co"
SUPABASE_KEY="your-supabase-anon-key"
```

### 2. Build the Docker Image

Navigate to the `movie-serving-api` directory and run the following command to build the Docker image. This command will install all dependencies inside the image.

```bash
docker build -t movie-recommendation-api .
```

### 3. Run the Docker Container

Once the image is built, you can run it as a container:

```bash
docker run -d -p 8000:8000 --env-file .env --name movie-api movie-recommendation-api
```

**Explanation of flags:**
- `-d`: Run the container in detached mode (in the background).
- `-p 8000:8000`: Map port 8000 on your host machine to port 8000 in the container.
- `--env-file .env`: Load the environment variables from your `.env` file into the container.
- `--name movie-api`: Give a convenient name to your container.

### 4. Access the API

The API should now be running!

- **Interactive Docs (Swagger UI)**: Open your browser and go to [http://localhost:8000/docs](http://localhost:8000/docs). You can test the endpoints directly from here.
- **Health Check**: Go to [http://localhost:8000/](http://localhost:8000/).

#### Example `curl` requests:

**By Title:**
```bash
curl -X GET "http://localhost:8000/api/v1/recommendations/by-title?title=Inception"
```

**By Text:**
```bash
curl -X GET "http://localhost:8000/api/v1/recommendations/by-text?query=a%20psychological%20thriller%20about%20dreams"
```

---

## 🐳 Docker Hub (CI/CD)

This repository can be configured with a CI/CD pipeline (e.g., using GitHub Actions in `.github/workflows/`) to automatically build and push the Docker image to a registry like Docker Hub whenever changes are merged into the main branch.

---

## 📊 Local Monitoring (Prometheus + Grafana + Loki)

This project includes a `docker-compose.monitoring.yml` file to run a full local monitoring stack alongside the API.

### 1. Run the Monitoring Stack

Use the following command to start the API, Prometheus, Grafana, and Loki:

```bash
# Ensure you have a .env file as described in "Getting Started"
docker-compose -f docker-compose.monitoring.yml up --build

#Stop the services
docker-compose -f docker-compose.monitoring.yml stop
```


### 2. Access the Services

Once everything is running, you can access the different services in your browser:

- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Prometheus**: [http://localhost:9090](http://localhost:9090)
- **Grafana**: [http://localhost:3000](http://localhost:3000) (Login with `admin` / `admin`)
- **API Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)

### 3. Monitoring Features

The API comes with comprehensive monitoring features:

- **Pre-configured Grafana Dashboard**: The monitoring setup includes a pre-configured dashboard with the following panels:
  - **API Request Rate**: Tracks the number of requests per minute to each endpoint
  - **Response Time**: Shows p50, p95, and p99 response time latencies
  - **Error Rate**: Visualizes the rate of error responses (4xx and 5xx status codes)
  - **Request/Response Size**: Monitors the size of requests and responses
  - **API Logs**: Displays real-time logs from the API service

- **Custom Metrics**:
  - Response time (latency) tracking across all endpoints
  - Request and response size monitoring
  - Error rate tracking with detailed status codes

All metrics are available through the `/metrics` endpoint and can be viewed in the pre-configured Grafana dashboard.
