# Simple Blog API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.1+-green.svg)](https://djangoproject.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-blue.svg)](https://github.com/astral-sh/ruff)

A robust Django-based blog REST API with secure authentication, HTTPS support, and comprehensive content management. Built with modern Python practices and production-ready deployment configuration.

## ✨ Features

- 🔐 **Secure Authentication**: Session-based authentication with CSRF protection
- 🔒 **HTTPS/SSL Support**: Self-signed certificates for development + Let's Encrypt ready for production
- 🐳 **Docker Ready**: Complete Docker and Docker Compose setup
- 📝 **Content Management**: Full CRUD operations for posts, categories, tags, and media files
- 👥 **User Management**: Role-based access control (Admin/Author) with profile management
- 📱 **Social Integration**: Social account management for author profiles
- 🌐 **RESTful API**: JSON:API specification compliant responses
- ⏱️ **Rate Limiting**: Configurable rate limits for authenticated and anonymous users
- 🔄 **API Versioning**: URL-based versioning for backward compatibility
- 🧪 **Test Suite**: Comprehensive test coverage with pytest
- ✨ **Code Quality**: Automated formatting and linting with ruff
- 📊 **Health Monitoring**: Built-in health check endpoint
- 📖 **Documentation**: Comprehensive API documentation

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Django 5.1
- **Database**: SQLite (PostgreSQL ready)
- **Web Server**: Nginx + Gunicorn
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest, pytest-django, factory_boy
- **Code Quality**: ruff, pre-commit hooks
- **Security**: HTTPS, CSRF protection, secure sessions

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended for quick setup)
- **Python 3.12+** (for local development)
- **OpenSSL** (for SSL certificate generation)

## 🚀 Quick Start

### Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd simple_blog
   ```

2. **Environment setup**
   ```bash
   cp .env.example .env.production
   # Edit .env.production with your settings
   ```

3. **Run with Docker**
   ```bash
   docker compose up -d
   ```

4. **Verify installation**
   ```bash
   curl -k https://localhost/health/
   ```

The API will be available at:
- **HTTPS**: https://localhost (production)
- **HTTP**: http://localhost (development)

### Manual Setup

For local development without Docker:

1. **Clone and setup Python environment**
   ```bash
   git clone <your-repo-url>
   cd simple_blog
   python3.12 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate   # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -e ".[dev,test]"
   ```

3. **Environment configuration**
   ```bash
   cp .env.example .env.local
   # Edit .env.local for development settings
   ```

4. **Database setup**
   ```bash
   mkdir -p storage/{data,static,media}
   chmod 755 storage/
   ./manage.py migrate
   ./manage.py createsuperuser
   ./manage.py collectstatic
   ```

5. **Run development server**
   ```bash
   ./manage.py runserver
   ```

## 📚 API Documentation

### Base URL

- **Production**: `https://localhost/api/v1`
- **Development**: `http://localhost:8000/api/v1`

### Authentication

The API uses session-based authentication with CSRF protection.

```bash
# Get CSRF token
curl -k -c cookies.txt -b cookies.txt https://localhost/api/v1/auth/csrf-token/

# Login
curl -k -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -H "Origin: https://localhost" \
  -H "Referer: https://localhost" \
  -c cookies.txt -b cookies.txt \
  -d '{"username":"admin","password":"your_password"}' \
  https://localhost/api/v1/auth/login/
```

### Core Endpoints

| Resource | Endpoint | Methods | Description |
|----------|----------|---------|-------------|
| **Health** | `/health/` | GET | System health check |
| **Categories** | `/api/v1/categories/` | GET, POST | Manage blog categories |
| **Categories** | `/api/v1/categories/{slug}/` | GET, PATCH, DELETE | Individual category operations |
| **Tags** | `/api/v1/tags/` | GET, POST | Manage blog tags |
| **Tags** | `/api/v1/tags/{slug}/` | GET, PATCH, DELETE | Individual tag operations |
| **Posts** | `/api/v1/posts/` | GET, POST | Manage blog posts |
| **Posts** | `/api/v1/posts/{slug}/` | GET, PATCH, DELETE | Individual post operations |
| **Media** | `/api/v1/posts/{slug}/media/` | GET, POST | Manage post media files |
| **Users** | `/api/v1/users/` | GET, POST | User management (admin only) |
| **Auth** | `/api/v1/auth/login/` | POST | User authentication |

### Query Parameters

**Posts filtering:**
- `?category=slug` - Filter by category
- `?tags=tag1,tag2` - Filter by tags (comma-separated)
- `?search=query` - Search in title and content

### Response Format

All responses follow JSON:API specification:

```json
{
  "data": {
    "type": "posts",
    "id": "1",
    "attributes": {
      "title": "Sample Post",
      "content": "Post content...",
      "status": "published",
      "created_at": "2024-01-15T10:30:45Z"
    },
    "relationships": {
      "author": {
        "data": {"type": "users", "id": "1"}
      }
    }
  }
}
```

### Complete API Reference

For detailed API documentation including all endpoints, parameters, and examples, see [API.md](API.md).

## 🏗️ Project Structure

```
simple_blog/
├── apps/                    # Django applications
│   ├── content/            # Blog content management
│   │   ├── models/         # Post, Category, Tag models
│   │   ├── views/          # API views
│   │   └── serializers/    # JSON:API serializers
│   ├── media_files/        # File upload handling
│   ├── users/              # User and profile management
│   └── utils/              # Shared utilities
├── simple_blog/            # Project configuration
│   ├── settings/          # Environment-specific settings
│   ├── urls.py            # URL routing
│   └── health.py          # Health check endpoint
├── tests/                  # Test suite
│   ├── factories/         # Test data factories
│   └── unit_tests/        # Unit tests
├── nginx/                  # Nginx configuration
│   ├── nginx.conf         # Server configuration
│   └── certs/             # SSL certificates
├── storage/               # Persistent data
│   ├── data/              # Database files
│   ├── media/             # User uploads
│   └── static/            # Static assets
├── docker-compose.yml     # Container orchestration
├── dockerfile             # Container image
├── pyproject.toml         # Project metadata
└── manage.py              # Django management
```

## 🧪 Development

### Running Tests

```bash
# With Docker
docker compose exec web python -m pytest

# Local development
pytest

# With coverage
pytest --cov=apps --cov-report=html
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Fix linting issues
ruff check --fix .
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

### Database Management

```bash
# Create migrations
./manage.py makemigrations

# Apply migrations
./manage.py migrate

# Create superuser
./manage.py createsuperuser

# Load sample data (if available)
./manage.py loaddata fixtures/sample_data.json
```

## 🔐 User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all resources and operations |
| **Author** | Create/edit own posts, manage own profile, upload media |
| **Anonymous** | Read access to published content only |

## 🔒 Security Features

- ✅ HTTPS/TLS encryption with configurable certificates
- ✅ CSRF protection for state-changing operations
- ✅ Secure session management
- ✅ Rate limiting to prevent abuse
- ✅ Input validation and sanitization
- ✅ SQL injection prevention via Django ORM
- ✅ XSS protection with proper output encoding
- ✅ Secure HTTP headers (HSTS, X-Frame-Options, etc.)

## 📊 Monitoring & Health Checks

### Health Check Endpoint

The `/health/` endpoint provides system status information:

```json
{
  "data": {
    "status": "ok",
    "timestamp": "2024-09-18T14:30:45.123456",
    "version": "0.1.0",
    "uptime_seconds": 3600,
    "database": {"status": "ok"},
    "environment": "production",
    "metrics": {
      "python_version": "3.12",
      "debug_mode": false
    }
  }
}
```

### Logging

```bash
# View application logs
docker compose logs web

# View nginx logs
docker compose logs nginx

# Follow logs in real-time
docker compose logs -f
```

## 🚀 Production Deployment

### SSL Certificate Setup

**Option 1: Let's Encrypt (Recommended for production)**

1. Uncomment the certbot service in `docker-compose.yml`
2. Update email and domain in the certbot configuration
3. Run: `docker compose up certbot`

**Option 2: Self-signed (Development)**

Self-signed certificates are generated automatically via the `certgen` service.

### Environment Variables

Key production settings in `.env.production`:

```env
# Security
SECRET_KEY=your-secure-secret-key
DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (optional: switch to PostgreSQL)
DJANGO_DB_ENGINE=django.db.backends.postgresql
DJANGO_DB_NAME=simple_blog
DJANGO_DB_USER=blog_user
DJANGO_DB_PASSWORD=secure_password
DJANGO_DB_HOST=db
DJANGO_DB_PORT=5432

# HTTPS
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
SECURE_SSL_REDIRECT=True
```

### Deployment Checklist

- [ ] Update `DJANGO_ALLOWED_HOSTS` with your domain
- [ ] Set a secure `SECRET_KEY`
- [ ] Configure proper SSL certificates
- [ ] Set `DEBUG=False`
- [ ] Configure backup strategy for database
- [ ] Set up monitoring and logging
- [ ] Configure domain DNS records
- [ ] Test all API endpoints after deployment

## 🛠️ Troubleshooting

### Common Issues

**Permission Errors**
```bash
sudo chown -R $USER:$USER storage/
chmod 755 storage/
```

**SSL Certificate Issues**
```bash
# Regenerate self-signed certificates
docker compose down
rm -rf nginx/certs/*
docker compose up -d
```

**Database Issues**
```bash
# Reset database (development only)
rm storage/data/db.sqlite3
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

**CSRF Token Errors**
- Ensure `Origin` and `Referer` headers match your domain
- Verify HTTPS is being used for secure cookies
- Check `CSRF_TRUSTED_ORIGINS` setting

### Debug Mode

For troubleshooting, temporarily enable debug mode:

```env
DEBUG=True
```

**⚠️ Remember to disable debug mode in production!**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run code quality checks (`ruff check .`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Use meaningful commit messages
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Jesús A. Perales** - *Initial work and maintenance*

## 🔗 Links

- [API Documentation](API.md) - Complete API reference
- [Change Log](API_CHANGES_SUMMARY.md) - Recent documentation updates
- [Issues](../../issues) - Report bugs or request features

## 📝 Changelog

### Version 0.1.0 (Current)
- Initial release with complete blog API functionality
- User authentication and authorization system
- Content management (posts, categories, tags)
- Media file handling
- Docker deployment setup
- Comprehensive test suite
- API documentation

---

**⭐ If this project helped you, please consider giving it a star!**
