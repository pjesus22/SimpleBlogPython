# Simple Blog

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Django-only blog API with secure authentication, HTTPS support, and Docker deployment configuration.

## Table of Contents

- [Simple Blog](#simple-blog)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Technology Stack](#technology-stack)
  - [Prerequisites](#prerequisites)
  - [Getting Started](#getting-started)
    - [Docker Setup (Recommended)](#docker-setup-recommended)
    - [Manual Setup](#manual-setup)
  - [API Documentation](#api-documentation)
    - [Response Format](#response-format)
    - [Error Handling](#error-handling)
    - [Rate Limiting](#rate-limiting)
    - [API Versioning](#api-versioning)
    - [Authentication](#authentication)
      - [Get CSRF Token](#get-csrf-token)
      - [Login](#login)
    - [API Endpoints](#api-endpoints)
      - [Categories](#categories)
    - [Example Responses](#example-responses)
      - [List Categories](#list-categories)
      - [Single Category](#single-category)
  - [Directory Structure](#directory-structure)
    - [Running Tests](#running-tests)
    - [Code Style](#code-style)
    - [Making Changes](#making-changes)
  - [Development Tools](#development-tools)
    - [API Documentation Endpoint](#api-documentation-endpoint)
    - [Health Check](#health-check)
  - [Production Deployment](#production-deployment)
  - [Security Considerations](#security-considerations)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Container Logs](#container-logs)
  - [Contributing](#contributing)
  - [License](#license)
  - [Security](#security)
  - [Changelog](#changelog)

## Features

- 🔐 Secure authentication system with session-based auth and CSRF protection
- 🔒 HTTPS/SSL support (self-signed default + Let's Encrypt/Certbot template)
- 🐳 Docker and Docker Compose setup
- 💾 Persistent data storage configuration
- 🚀 Production-ready configuration with Gunicorn and Nginx
- 📝 Content management system with categories, posts, and tags
- 🌐 RESTful API with proper response formatting and error handling
- ⏱️ Rate limiting for both authenticated and anonymous users
- 🔄 API versioning (v1, v2)
- 🧪 Test suite with pytest
- ✨ Code quality checks with ruff
- 📖 Documentation with detailed setup and usage instructions

## Technology Stack

- Python 3.12
- Django 5.1
- SQLite Database
- Nginx
- Docker & Docker Compose
- Gunicorn

## Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- OpenSSL (for certificate generation)

## Getting Started

### Docker Setup (Recommended)

1. **Clone the Repository**

   ```bash
   git clone https://github.com/{YOUR_USERNAME}/simple_blog.git
   cd simple_blog
   ```

2. **Environment Setup**

   Create either a `.env.production` or `.env.local` file (or both) from the example:

   ```bash
   cp .env.example .env.production
   # Edit the .env file with your preferred settings
   ```

3. **Build and Run with Docker**

   ```bash
   docker compose up -d
   ```

4. **Test the application**

   Test the application is running at `http://localhost/health`.

### Manual Setup

If you prefer to run the application without Docker, follow these steps:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/{YOUR_USERNAME}/blog_apiv2.git
   cd blog_apiv2
   ```

2. **Set Up Python Environment**

   Ensure you have Python 3.12 installed, then create a virtual environment:

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**

   ```bash
   pip install -e ".[dev,test]"
   ```

4. **Environment Setup**

   Create a `.env.production` or `.env.local` file (or both) from the example:

   ```bash
   cp .env.example .env.production # Edit .env file with your preferred settings
   ```

5. **Create Storage Directories**

   ```bash
   mkdir -p storage/{data,static,media}
   chmod -R 777 storage/
   ```

6. **Run Database Migrations**

   ```bash
   ./manage.py migrate
   ```

7. **Create Superuser**

   ```bash
   ./manage.py createsuperuser
   ```

8. **Collect Static Files**

   ```bash
   ./manage.py collectstatic
   ```

9. **Generate SSL Certificates (Optional)**

   For local development, you can generate self-signed SSL certificates:

   ```bash
   mkdir -p nginx/certs
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout nginx/certs/nginx.key -out nginx/certs/nginx.crt \
       -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
       -addext "subjectAltName = DNS:localhost,IP:127.0.0.1"
   ```

10. **Run the Development Server**

    ```bash
    ./manage.py runserver
    ```

    The application should now be running at `http://localhost:8000`.

11. **Setting Up Nginx** (Optional)

    If you want to use Nginx:

    - Install Nginx on your system
    - Copy the Nginx configuration

      ```bash
      sudo cp nginx/nginx.conf /etc/nginx/sites-available/simple_blog
      sudo ln -s /etc/nginx/sites-available/simple_blog /etc/nginx/sites-enabled/
      ```

    - Modify the Nginx configuration to point to your local setup.
    - Restart Nginx:

      ```bash
      sudo service nginx restart
      ```

12. **Running with Gunicorn**

    For a more production-like setup, use Gunicorn:

    ```bash
    gunicorn simple_blog.wsgi:application -c gunicorn.conf.py
    ```

Note: Ensure all necessary environment variables are set in your .env.local file. You may need to adjust paths and settings based on your specific local environment.

## API Documentation

### Response Format

All API responses follow the JSON:API specification:

```json
{
    "data": {
        "type": "categories",
        "id": "1",
        "attributes": {
            "name": "Category Name",
            "description": "Category Description",
            "slug": "category-name",
            "created_at": "2025-04-20T16:13:11.482Z",
            "updated_at": "2025-04-20T16:13:11.482Z"
        },
        "relationships": {}
    }
}
```

### Error Handling

API errors follow a consistent format:

```json
{
    "error": {
        "code": "error_code",
        "message": "Human-readable error message",
        "details": {}
    }
}
```

Common HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

### Rate Limiting

The API implements rate limiting to prevent abuse:

- Authenticated users: 100 requests per minute
- Anonymous users: 20 requests per minute

Rate limit headers are included in all responses:

- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

### API Versioning

The API uses URL versioning (e.g., `/api/v1/`). Major versions may include breaking changes:

- v1: Current stable version
- v2: This version (includes breaking changes from v1)

### Authentication

The API uses session-based authentication with CSRF protection.

#### Get CSRF Token

```bash
curl -k -c cookies.txt -b cookies.txt https://localhost/api/v1/auth/csrf-token/
```

#### Login

```bash
curl -k -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -H "Referer: https://localhost" \
  -H "Origin: https://localhost" \
  -c cookies.txt \
  -b cookies.txt \
  -d '{"username":"<username>","password":"<password>"}' \
  https://localhost/api/v1/auth/login/
```

### API Endpoints

#### Categories

- List Categories: `GET /api/v1/categories/`
- Create Category: `POST /api/v1/categories/`
- Get Category: `GET /api/v1/categories/{id}/`
- Update Category: `PUT /api/v1/categories/{id}/`
- Delete Category: `DELETE /api/v1/categories/{id}/`

Request example:

```bash
curl -k -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -H "Referer: https://localhost" \
  -H "Origin: https://localhost" \
  -c cookies.txt \
  -b cookies.txt \
  -d '{"name":"Category Name", "description":"Category Description"}' \
  https://localhost/api/v1/categories/
```

### Example Responses

#### List Categories

```json
{
    "data": [
        {
            "type": "categories",
            "id": "1",
            "attributes": {
                "name": "Technology",
                "description": "Tech-related posts",
                "slug": "technology",
                "created_at": "2025-04-20T16:13:11.482Z",
                "updated_at": "2025-04-20T16:13:11.482Z"
            },
            "relationships": {}
        }
    ],
    "meta": {
        "total": 1,
        "page": 1,
        "per_page": 10
    }
}
```

#### Single Category

```json
{
    "data": {
        "type": "categories",
        "id": "1",
        "attributes": {
            "name": "Technology",
            "description": "Tech-related posts",
            "slug": "technology",
            "created_at": "2025-04-20T16:13:11.482Z",
            "updated_at": "2025-04-20T16:13:11.482Z"
        },
        "relationships": {}
    }
}
```

## Directory Structure

blog_apiv2/
├── apps/
│   ├── content/          # Content management app
│   ├── media_files/      # Media files handling
│   └── users/            # User management
├── docs/               # Project documentation
│   ├── changelog.md    # Version history
│   ├── contributing.md # Contribution guidelines
│   └── security.md     # Security policy
├── nginx/
│   ├── certs/           # SSL certificates
│   └── nginx.conf       # Nginx configuration
├── simple_blog/         # Project configuration
├── storage/
│   ├── data/           # Database files (SQLite)
│   ├── media/          # User uploaded files
│   └── static/         # Static files
├── tests/              # Test suite
├── .env.production     # Production Environment variables
├── .env.local          # Local Enviroment variables
├── .env.example        # Example environment variables
├── docker-compose.yml  # Docker compose configuration
├── Dockerfile          # Docker build configuration
└── README.md           # Project overview

### Running Tests

```bash
docker compose exec web python manage.py test
```

### Code Style

The project uses ruff for code formatting and linting:

```bash
ruff check .
ruff format .
```

### Making Changes

1. Create a new branch
2. Make your changes
3. Write/update tests
4. Run the test suite
5. Submit a pull request

## Development Tools

### API Documentation Endpoint

The API documentation is available at `/api/docs/` when the server is running. It provides:

- Interactive API testing
- Schema details
- Authentication information
- Example requests and responses

### Health Check

A health check endpoint is available at `/health/` to verify system status. It returns:

```json
{
  "data": {
    "status": "ok",
    "timestamp": "2025-04-21T21:00:00.000000",
    "version": "0.1.0",
    "uptime_seconds": 1234,
    "database": {
      "status": "ok"
    },
    "environment": "production",
    "metrics": {
      "python_version": "3.12",
      "debug_mode": false
    }
  }
}
```

## Production Deployment

For production deployment:

1. Use proper SSL certificates instead of self-signed ones
2. Set appropriate environment variables
3. Configure proper domain names

## Security Considerations

- SSL/TLS encryption enabled
- CSRF protection
- Secure session handling
- No sensitive data in version control
- Proper file permissions

## Troubleshooting

### Common Issues

1. **Permission Denied for Storage Directory**

   ```bash
   sudo chown -R $USER:$USER storage/
   chmod -R 777 storage/
   ```

2. **SSL Certificate Issues**

   ```bash
   # Regenerate certificates
   rm -rf nginx/certs/*
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout nginx/certs/private.key \
       -out nginx/certs/certificate.crt \
       -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
   ```

3. **Database Connection Issues**

   - Check if the SQLite database file exists in `storage/data`
   - Ensure proper permissions on the storage directory
   - Verify SQLite database settings in `.env` file

4. **CSRF Token Errors**

   - Ensure you're including the Referer and Origin headers
   - Check that the CSRF token in the header matches the cookie
   - Verify you're using HTTPS

### Container Logs

View container logs:

```bash
# All logs
docker compose logs

# Specific service
docker compose logs web
docker compose logs nginx
```

## Contributing

Please see [Contributing Guidelines](docs/contributing.md) for detailed information on:

- Setting up the development environment
- Coding standards
- Pull request process
- Testing requirements
- Commit message guidelines
- Branch naming conventions

## License

[MIT License](LICENSE)

## Security

Please see our [Security Policy](docs/security.md) for information on reporting security vulnerabilities.

## Changelog

For version history and release notes, see the [Changelog](docs/changelog.md).
