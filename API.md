# Simple Blog API Documentation

## Overview

This document provides detailed information about the Simple Blog API, including authentication, endpoints, request/response formats, and examples.

## Table of Contents

- [Simple Blog API Documentation](#simple-blog-api-documentation)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Base URL](#base-url)
  - [Authentication](#authentication)
    - [Roles and Permissions](#roles-and-permissions)
    - [Get CSRF Token](#get-csrf-token)
    - [Login](#login)
    - [Logout](#logout)
  - [Data Formats](#data-formats)
    - [DateTime Format](#datetime-format)
    - [Pagination](#pagination)
    - [File Upload Constraints](#file-upload-constraints)
  - [Response format](#response-format)
  - [Error Handling](#error-handling)
  - [Rate Limiting](#rate-limiting)
  - [API Versioning](#api-versioning)
  - [Health Check](#health-check)
  - [Endpoints](#endpoints)
    - [Categories](#categories)
      - [List categories](#list-categories)
      - [Create category](#create-category)
      - [Retrieve category](#retrieve-category)
      - [Update category](#update-category)
      - [Delete category](#delete-category)
    - [Tags](#tags)
      - [List tags](#list-tags)
      - [Create tag](#create-tag)
      - [Retrieve tag](#retrieve-tag)
      - [Update tag](#update-tag)
      - [Delete tag](#delete-tag)
    - [Media files](#media-files)
      - [List media files (global)](#list-media-files-global)
      - [List media files (from post)](#list-media-files-from-post)
      - [Retrieve media file (global)](#retrieve-media-file-global)
      - [Retrieve media file (from post)](#retrieve-media-file-from-post)
      - [Create media files](#create-media-files)
      - [Delete media files](#delete-media-files)
    - [Users](#users)
      - [List users](#list-users)
      - [Retrieve user](#retrieve-user)
      - [Create users](#create-users)
      - [Update users (base)](#update-users-base)
      - [Request Example](#request-example)
      - [Response Example](#response-example)
      - [Update users (profiles)](#update-users-profiles)
      - [Create social networks](#create-social-networks)
      - [Update social networks](#update-social-networks)
      - [Delete social networks](#delete-social-networks)
      - [Delete users](#delete-users)
    - [Posts](#posts)
      - [List posts](#list-posts)
      - [Retrieve posts](#retrieve-posts)
      - [Create posts](#create-posts)
      - [Update posts](#update-posts)
      - [Delete posts](#delete-posts)

## Base URL

The base URL for all API endpoints is:

```bash
https://localhost/api/v1
```

**Note**: When running the application in local (development) mode, use:

```bash
http://localhost:8000/api/v1
```

(The production environment doesn't support HTTP for localhost connections).

## Authentication

The API uses session-based authentication with CSRF protection.

### Roles and Permissions

| Role      | Description                | Example Endpoints Access         |
|-----------|----------------------------|----------------------------------|
| Admin     | Full access                | All endpoints                    |
| Author    | CRUD on own posts, profile | Posts, profile, media            |
| User      | Read-only                  | Public endpoints (GET)           |
| Anonymous | Limited read-only          | Public endpoints (GET, limited)  |

### Get CSRF Token

```bash
curl -k -L 'https://localhost/api/v1/auth/csrf-token/' \
  -c cookies.txt -b cookies.txt
```

### Login

```bash
curl -k -L 'https://localhost/api/v1/auth/login/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost' \
  -d '{"username": "<username>", "password": "<password>"}'
```

### Logout

```bash
curl -k -L -X POST 'https://localhost/api/v1/auth/logout/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost'
```

## Data Formats

### DateTime Format

All datetime fields in the API use ISO 8601 format with UTC timezone:

```text
YYYY-MM-DDTHH:MM:SSZ
```

**Example:**

```text
2024-01-15T10:30:45Z
```

### Pagination

The API does not currently implement pagination. All list endpoints return complete result sets. Future versions may include pagination with the following structure:

```json
{
  "data": [...],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 25,
      "total": 100,
      "total_pages": 4
    }
  }
}
```

### File Upload Constraints

Media file uploads have the following constraints:

**Supported File Types:**

- **Images**: jpg, jpeg, png, gif, webp
- **Videos**: mp4, webm
- **Audio**: mp3, aac, wav, ogg

**File Size Limits:**

- Maximum file size: Based on server configuration (typically 10MB)
- Files are automatically categorized by extension
- Image files include automatic width/height metadata extraction

**Validation Rules:**

- File names must be unique within each post
- Only authenticated users can upload files
- Files are associated with specific posts upon upload

## Response format

All API responses follow the JSON:API specification:

```json
{
  "data": {
    "type": "resource_type",
    "id": "resource_id",
    "attributes": {
      "field1": "value1",
      "field2": "value2"
    },
    "relationships": {
      "relationship1": {
        "data": [
          {
            "type": "related_resource_type1",
            "id": "related_resource_id1"
          }
        ]
      }
    }
  }
}
```

## Error Handling

API errors follow a consistent format:

```json
{
  "errors": [
    {
      "status": "error_status_code",
      "title": "generic_error_title",
      "detail": "human-readable_error_message",
      "meta": {
        "info": "additional_error_info"
      }
    }
  ]
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

**Example error response for missing field:**

```json
{
  "errors": [
    {
      "status": "400",
      "title": "Validation Error",
      "detail": "The 'name' field is required.",
      "meta": {
        "field": "name"
      }
    }
  ]
}
```

## Rate Limiting

- Authenticated users: 100 requests per minute
- Anonymous users: 20 requests per minute

Rate limit headers:

- X-RateLimit-Limit: Maximum requests per window
- X-RateLimit-Remaining: Remaining requests in current window
- X-RateLimit-Reset: Time when the rate limit resets

**Example response headers:**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 98
X-RateLimit-Reset: 1713720000
```

## API Versioning

The API uses URL versioning (e.g., `/api/v1/`). Major versions may include breaking changes:

- v1: Current stable version

## Health Check

The API provides a health check endpoint that can be used to verify the system's operational status.

**Method:** `GET`

**Endpoint:** `/health/`

**Authentication required:** None

**Response example:**

```json
{
  "data": {
    "status": "ok",
    "timestamp": "2024-09-18T14:30:45.123456",
    "version": "0.1.0",
    "uptime_seconds": 3600,
    "database": {
      "status": "ok"
    },
    "environment": "production",
    "metrics": {
      "python_version": "3.11",
      "debug_mode": false
    }
  }
}
```

**Error Response (when service is unhealthy):**

```json
{
  "data": {
    "status": "error",
    "timestamp": "2024-09-18T14:30:45.123456",
    "version": "0.1.0",
    "uptime_seconds": 3600,
    "database": {
      "status": "error",
      "message": "database connection error"
    },
    "environment": "production",
    "metrics": {
      "python_version": "3.11",
      "debug_mode": false
    }
  }
}
```

**Status Codes:**
- 200: System is healthy
- 503: One or more components are unhealthy

## Endpoints

### Categories

#### List categories

**Method:** `GET`

**Endpoint:** `/api/v1/categories/`

**Authentication required:** None

**Query Parameters:** None

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/categories/'
```

**Response example:**

```json
{
   "data":[
      {
         "type":"categories",
         "id":"1",
         "attributes":{
            "name":"<category_name>",
            "description":"<category_description>",
            "slug":"<category_slug>",
            "created_at":"<datetime_object>",
            "updated_at":"<datetime_object>"
         },
         "relationships":{
            "posts":{
               "data":[
                  {
                     "type":"posts",
                     "id":"1"
                  }
               ]
            }
         }
      }
   ]
}
```

#### Create category

**Method:** `POST`

**Endpoint:** `/api/v1/categories/`

**Authentication required:** admin required

**Parameters:**

| Field       | Type   | Required | Max Length | Allowed Values | Description             |
|-------------|--------|----------|------------|----------------|-------------------------|
| name        | string | Yes      | 50         | -              | Category name (unique)  |
| description | string | No       | 255        | -              | Category description    |

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/categories/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost' \
  -d '{
    "name":"<category_name>",
    "description":"<category_description>"
  }'
```

**Response example:**

```json
{
  "data": {
    "type": "categories",
    "id": "1",
    "attributes": {
        "name": "<category_name>",
        "description": "<category_description>",
        "slug": "<category_slug>",
        "created_at": "<datetime_object>",
        "updated_at": "<datetime_object>"
    },
    "relationships": {}
  }
}
```

**Common errors:**

- **400 Bad Request:** Missing required fields.
- **403 Forbidden:** Not authenticated as admin.

```json
{
  "errors": [
    {
      "status": "403",
      "title": "Forbidden",
      "detail": "You do not have permission to perform this action.",
      "meta": {}
    }
  ]
}
```

#### Retrieve category

**Method:** GET

**Endpoint:** `/api/v1/categories/<category_slug>/`

**Authentication required:** None

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/categories/<category_slug>/'
```

**Response example:**

```json
{
  "data":{
    "type":"categories",
    "id":"1",
    "attributes":{
        "name":"<category_name>",
        "description":"<category_description>",
        "slug":"<category_slug>",
        "created_at":"<datetime_object>",
        "updated_at":"<datetime_object>"
    },
    "relationships":{
        "posts":{
          "data":[
              {
                "type":"posts",
                "id":"1"
              }
          ]
        }
    }
  },
  "included":[
    {
        "type":"posts",
        "id":"1",
        "attributes":{
          "title":"<post_title>",
          "content":"<post_content>",
          "slug":"<post_slug>",
          "created_at":"<datetime_object>",
          "updated_at":"<datetime_object>"
        }
    }
  ]
}
```

#### Update category

**Method:** PATCH

**Endpoint:** `/api/v1/categories/<category_slug>/`

**Authentication required:** admin required

**Request example:**

```bash
curl -k -L -X PATCH 'https://localhost/api/v1/categories/<category_slug>/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost' \
  -d '{
    "name":"<category_name>",
    "description":"<category_description>"
  }'

```

**Response example:**

```json
{
  "data":{
      "type":"categories",
      "id":"1",
      "attributes":{
         "name":"<category_name>",
         "description":"<category_description>",
         "slug":"<category_slug>",
         "created_at":"<datetime_object>",
         "updated_at":"<datetime_object>"
      },
      "relationships":{}
  }
}
```

#### Delete category

**Method:** `DELETE`

**Endpoint:** `/api/v1/categories/<category_slug>/`

**Authentication required:** admin required

**Request example:**

```bash
curl -k -L -X DELETE 'https://localhost/api/v1/categories/<category_slug>/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost'
```

**Response example:**

```http
204 No Content
```

### Tags

#### List tags

**Method:** `GET`

**Endpoint:** `/api/v1/tags/`

**Query Parameters:** None

**Authentication required:** None

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/tags/'
```

**Response example:**

```json
{
  "data":[
    {
      "type":"tags",
      "id":"1",
      "attributes":{
        "name":"<tag_name>",
        "slug":"<tag_slug>",
        "created_at":"<datetime_object>",
        "updated_at":"<datetime_object>"
      },
      "relationships":{
        "posts":{
          "data":[
            {
              "type":"posts",
              "id":"1"
            }
          ]
        }
      }
    }
  ]
}
```

#### Create tag

**Method:** `POST`

**Endpoint:** `/api/v1/tags/`

**Authentication required:** admin required

**Parameters:**

| Field | Type   | Required | Max Length | Allowed Values | Description |
|-------|--------|----------|------------|----------------|-------------|
| name  | string | Yes      | 50         | -              | Tag name    |

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/tags/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost' \
  -d '{
    "name":"<tag_name>"
  }'
```

**Response example:**

```json
{
  "data":{
    "type":"tags",
    "id":"1",
    "attributes":{
      "name":"<tag_name>",
      "slug":"<tag_slug>",
      "created_at":"<datetime_object>",
      "updated_at":"<datetime_object>"
    },
    "relationships":{}
  }
}
```

**Common errors:**

- **400 Bad Request:** Missing required fields.
- **403 Forbidden:** Not authenticated as admin.

```json
{
  "errors": [
    {
      "status": "400",
      "title": "Validation Error",
      "detail": "The 'name' field is required.",
      "meta": {
        "field": "name"
      }
    }
  ]
}
```

#### Retrieve tag

**Method:** GET

**Endpoint:** `/api/v1/tags/<tag_slug>/`

**Authentication required:** None

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/tags/<tag_slug>/'
```

**Response example:**

```json
{
  "data": {
    "type": "tags",
    "id": "1",
    "attributes": {
        "name": "<tag_name>",
        "slug": "<tag_slug>",
        "created_at": "<datetime_object>",
        "updated_at": "<datetime_object>"
    },
    "relationships": {
      "posts": {
        "data": [
          {
            "type": "posts",
            "id": "1"
          }
        ]
      }
    }
  },
  "included": [
    {
      "type": "posts",
      "id": "1",
      "attributes": {
        "title": "<post_title>",
        "content": "<post_content>",
        "slug": "<post_slug>",
        "created_at": "<datetime_object>",
        "updated_at": "<datetime_object>"
      }
    }
  ]
}
```

#### Update tag

**Method:** PATCH

**Endpoint:** `/api/v1/tags/<tag_slug>/`

**Authentication required:** admin required

**Request example:**

```bash
curl -k -L -X PATCH 'https://localhost/api/v1/tags/<tag_slug>/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost' \
  -d '{
    "name":"<tag_name>"
  }'

**Response example:**

```json
{
  "data": {
    "type": "tags",
    "id": "1",
    "attributes": {
        "name": "<tag_name>",
        "slug": "<tag_slug>",
        "created_at": "<datetime_object>",
        "updated_at": "<datetime_object>"
    },
    "relationships": {}
  }
}
```

#### Delete tag

**Method:** `DELETE`

**Endpoint:** `/api/v1/tags/<tag_slug>/`

**Authentication required:** admin required

**Request example:**

```bash
curl -k -L -X DELETE 'https://localhost/api/v1/tags/<tag_slug>/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost'
```

**Response example:**

```http
204 No Content
```

### Media files

#### List media files (global)

**Method:** `GET`

**Endpoint:** `/api/v1/media/`

**Authentication required:** admin required

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/media/' \
  -c cookies.txt -b cookies.txt
```

**Response example:**

```json
{
  "data": [
    {
      "type": "media_files",
      "id": "1",
      "attributes": {
        "name": "<file_name>",
        "file": "<file_path>",
        "type": "<file_type>",
        "size": "<file_size>",
        "width": "<file_width>",
        "height": "<file_height>",
        "created_at": "<datetime_object>",
        "updated_at": "<datetime_object>"
      },
      "relationships": {
        "post": {
          "data": {
            "type": "posts",
            "id": "1"
          }
        }
      }
    }
  ]
}
```

#### List media files (from post)

**Method:** `GET`

**Endpoint:** `/api/v1/posts/<post_slug>/media/`

**Authentication required:**

- None for posts with public status  (returns general info only)
- Admin or post author for posts with private status (returns detailed info)

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/posts/<post_slug>/media/' \
  -c cookies.txt -b cookies.txt
```

**Response example:**

```json
{
  "data": [
    {
      "type": "media_files",
      "id": "1",
      "attributes": {
        "type": "<file_type>",
        "file": "<file_path>",
        "created_at": "<datetime_object>",
        "updated_at": "<datetime_object>"
      },
      "relationships": {
        "post": {
          "data": {
            "type": "posts",
            "id": "1"
          }
        }
      }
    }
  ]
}
```

#### Retrieve media file (global)

**Method:** `GET`

**Endpoint:** `/api/v1/media/<media_id>/`

**Authentication required:** Admin required

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/media/<media_id>/' \
  -c cookies.txt -b cookies.txt
```

**Response example:**

```json
{
    "data": {
        "type": "media_files",
        "id": "1",
        "attributes": {
            "type": "<file_type>",
            "file": "<file_path>",
            "created_at": "<datetime_object>",
            "updated_at": "<datetime_object>",
            "name": "<file_name>",
            "size": "<file_size>",
            "width": "<file_width>",
            "height": "<file_height>"
        },
        "relationships": {
            "post": {
                "data": {
                    "type": "posts",
                    "id": "1"
                }
            }
        }
    }
}
```

#### Retrieve media file (from post)

**Method:** `GET`

**Endpoint:** `/api/v1/posts/<post_slug>/media/<id>/`

**Authentication required:**

- None for posts with public status  (returns general info only)
- Admin or post author for posts with private status (returns detailed info)

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/posts/<post_slug>/media/<id>/'
  -c cookies.txt -b cookies.txt
```

**Response example:**

```json
{
    "data": {
        "type": "media_files",
        "id": "1",
        "attributes": {
            "type": "<file_type>",
            "file": "<file_path>",
            "created_at": "<datetime_object>",
            "updated_at": "<datetime_object>",
            "name": "<file_name>",
            "size": "<file_size>",
            "width": "<file_width>",
            "height": "<file_height>"
        },
        "relationships": {
            "post": {
                "data": {
                    "type": "posts",
                    "id": "1"
                }
            }
        }
    }
}
```

#### Create media files

**Method:** `POST`

**Endpoint:** `/api/v1/posts/<post_slug>/media/`

**Authentication:** admin or post author required

**Parameters:**

| Field | Type   | Required | Allowed Values | Description                       |
|-------|--------|----------|----------------|-----------------------------------|
| files | file[] | Yes      | jpg,jpeg,png,gif,webp,mp4,webm,mp3,aac,wav,ogg | One or more files to attach       |

**Request Example:**

```bash
curl -k -X POST \
  -L 'https://localhost/api/v1/posts/<post_slug>/media/' \
  -c cookies.txt -b cookies.txt \
  -H 'X-CSRFToken: <csrf_token>' \
  -F 'files=@path/to/file.ext'
```

**Response Example:**

```json
{
   "data":[
      {
         "type":"media_files",
         "id":"1",
         "attributes":{
            "name":"<file_name>",
            "file":"<file_path>",
            "type":"<file_type>",
            "size":"<file_size>",
            "width": "<file_width>",
            "height": "<file_height>",
            "created_at": "<datetime_object>",
            "updated_at": "<datetime_object>"
         },
         "relationships":{
            "post":{
               "data":{
                  "type":"posts",
                  "id":"1"
               }
            }
         }
      }
   ]
}
```

#### Delete media files

**Method:** `DELETE`

**Endpoint:** `/api/v1/posts/<post_slug>/media/<id>/`

**Authentication required:** admin or post author required

**Request example:**

```bash
curl -k -X DELETE \
  -L 'https://localhost/api/v1/posts/<post_slug>/media/<id>/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost'
```

**Response example:**

```http
204 No Content
```

### Users

#### List users

**Method:** `GET`

**Endpoint:** `/api/v1/users/`

**Authentication required:** admin

**Request example:**

```bash
curl -k -L 'https://localhost/api/v1/users/' \
  -c cookies.txt -b cookies.txt
```

**Response example:**

```json
{
  "data": [
    {
      "type": "users",
      "id": "1",
      "attributes": {
        "username": "<username>",
        "first_name": "<user_first_name>",
        "last_name": "<user_last_name>",
        "email": "<user_email>",
        "is_active": "<bool>",
        "date_joined": "<datetime_object>",
        "role": "<user_role>"
      }
    }
  ]
}
```

#### Retrieve user

**Method:** `GET`

**Endpoint:** `/api/v1/users/<user_id>/`

**Authentication required:** admin or own user required

Request example:

```bash
curl -k -L 'https://localhost/api/v1/users/<user_id>/' \
  -c cookies.txt -b cookies.txt
```

Response example:

```json
{
    "data": {
        "type": "users",
        "id": "1",
        "attributes": {
          "username": "<username>",
          "first_name": "<user_first_name>",
          "last_name": "<user_last_name>",
          "email": "<user_email>",
          "is_active": "<bool>",
          "date_joined": "<datetime_object>",
          "role": "<user_role>"
        },
        "relationships": {
            "profile": {
                "data": {
                    "type": "author-profiles",
                    "id": "1"
                }
            },
            "posts": {
                "data": [
                    {
                        "type": "posts",
                        "id": "1"
                    }
                ]
            }
        }
    },
    "included": [
        {
            "type": "author-profiles",
            "id": "1",
            "attributes": {
                "bio": "<biography paragraph>",
                "profile_picture": "<profile_picture_path>"
            },
            "relationships": {
                "social-accounts": {
                    "data": [
                        {
                            "type": "social-accounts",
                            "id": "1"
                        }
                    ]
                }
            }
        }
    ]
}
```

#### Create users

**Method:** `POST`

**Endpoint:** `/api/v1/users/`

**Authentication required:** admin required

**Parameters:**

| Field      | Type   | Required | Max Length | Allowed Values | Description             |
|------------|--------|----------|------------|----------------|-------------------------|
| username   | string | Yes      | 150        | -              | Unique username         |
| password   | string | Yes      | 128        | -              | User password           |
| email      | string | Yes      | 254        | -              | User email              |
| first_name | string | No       | 30         | -              | First name              |
| last_name  | string | No       | 150        | -              | Last name               |

**Request Example:**

```bash
curl -k -X POST \
  -L 'https://localhost/api/v1/users/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -d '{
    "username": "<user_name>",
    "password": "<user_password>",
    "email": "<user_email>",
    "first_name": "<user_first_name>",
    "last_name": "<user_last_name>",
  }'
```

Note: fields `username`, `password` and `email` are mandatory, otherwise an exception 400 will be thrown.
Note #2: This method only creates users with the author role, admin users must be created using django's default `./manage.py createsuperuser` command.

**Response Example:**

```json
{
   "data":{
      "type":"users",
      "id":"1",
      "attributes":{
         "username":"<username>",
         "first_name":"<user_first_name>",
         "last_name":"<user_last_name>",
         "email":"<user_email>",
         "is_active":"<bool>",
         "date_joined":"<datetime_object>",
         "role":"<user_role>"
      },
      "relationships":{
         "profile":{
            "data":{
               "type":"author-profiles",
               "id":"1"
            }
         }
      }
   },
   "included":[
      {
         "type":"author-profiles",
         "id":"1",
         "attributes":{
            "bio":"<biography_paragraph>",
            "profile_picture":"<profile_picture_path>"
         }
      }
   ]
}
```

**Common errors:**

- **400 Bad Request:** Missing required fields.
- **403 Forbidden:** Not authenticated as admin.

```json
{
  "errors": [
    {
      "status": "400",
      "title": "Validation Error",
      "detail": "Username already exists",
      "meta": {}
    }
  ]
}
```

#### Update users (base)

**Method:** `PATCH`

**Endpoint:** `/api/v1/users/<user_id>/`

**Authentication required:** admin or own user

#### Request Example

```bash
curl -k -X PATCH \
  -L 'https://localhost/api/v1/users/<user_id>/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -d '{
    "username": "<user_name>",
    "password": "<user_password>",
    "email": "<user_email>",
    "first_name": "<user_first_name>",
    "last_name": "<user_last_name>"
  }'
```

#### Response Example

```json
{
   "data":{
      "type":"users",
      "id":"1",
      "attributes":{
         "username":"<username>",
         "first_name":"<user_first_name>",
         "last_name":"<user_last_name>",
         "email":"<user_email>",
         "is_active":"<bool>",
         "date_joined":"<datetime_object>",
         "role":"<user_role>"
      },
      "relationships":{
         "profile":{
            "data":{
               "type":"author-profiles",
               "id":"1"
            }
         }
      }
   },
   "included":[
      {
         "type":"author-profiles",
         "id":"1",
         "attributes":{
            "bio":"<biography_paragraph>",
            "profile_picture":"<profile_picture_path>"
         }
      }
   ]
}
```

#### Update users (profiles)

**Method:** `PATCH`

**Endpoint:** `/api/v1/users/<user_id>/profile/`

**Authentication required:** admin or own user

**Request Example:**

```bash
curl -k -X PATCH \
  -L 'https://localhost/api/v1/users/<user_id>/profile/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -d '{"bio":"<test_bio_description>"}'
```

**Response Example:**

```json
{
  "data": {
    "type": "author-profiles",
    "id": "1",
    "attributes": {
      "bio": "<test_bio_description>",
      "profile_picture": "<profile_picture_path>"
    },
    "relationships": {
      "user": {
        "data": {
          "type": "users",
          "id": "1"
        }
      }
    }
  }
}
```

#### Create social networks

**Method:** `POST`

**Endpoint:** `/api/v1/users/<user_id>/social-accounts/`

**Authentication required:** admin or own user

**Request Example:**

```bash
curl -k -X POST \
  -L 'https://localhost/api/v1/users/1/social-accounts/' \
  -c cookies.txt -b cookies.txt \
  -H 'X-CSRFToken: <csrf_token>' \
  -F 'provider=twitter' \
  -F 'username=example_user' \
  -F 'url=https://twitter.com/example_user'
```

#### Update social networks

**Method:** `PATCH`

**Endpoint:** `/api/v1/users/<user_id>/social-accounts/<social_id>/`

**Authentication required:** admin or own user

**Request Example:**

```bash
curl -k -X PATCH \
  -L 'https://localhost/api/v1/users/1/social-accounts/1/' \
  -c cookies.txt -b cookies.txt \
  -H 'X-CSRFToken: <csrf_token>' \
  -F 'provider=twitter' \
  -F 'username=example_user' \
  -F 'url=https://twitter.com/example_user'
```

#### Delete social networks

**Method:** `DELETE`

**Endpoint:** `/api/v1/users/<user_id>/social-accounts/<social_id>/`

**Authentication required:** admin or own user

**Request example:**

```bash
curl -k -X DELETE \
  -L 'https://localhost/api/v1/users/<user_id>/social-accounts/<social_id>/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost'
```

#### Delete users

**Method:** `DELETE`

**Endpoint:** `/api/v1/users/<user_id>/`

**Authentication required:** admin

**Request example:**

```bash
curl -k -X DELETE \
  -L 'https://localhost/api/v1/users/<user_id>/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost'
```

**Response example:**

```http
204 No Content
```

### Posts

#### List posts

**Method:** `GET`

**Endpoint:** `/api/v1/posts/`

**Authentication:**

- None for posts with public status
- Admin or author for posts with private status

**Query Parameters:**

| Parameter | Type   | Description                              | Example                    |
|-----------|--------|------------------------------------------|----------------------------|
| category  | string | Filter by category slug                  | `?category=technology`     |
| tags      | string | Filter by tag slugs (comma-separated)   | `?tags=python,django`      |
| search    | string | Search in title and content             | `?search=tutorial`         |

**Field Constraints:**

| Field    | Type   | Required | Max Length | Allowed Values                      | Description                 |
|----------|--------|----------|------------|-------------------------------------|--------------------------|
| title    | string | Yes      | 50         | -                                   | Post title               |
| content  | text   | No       | unlimited  | -                                   | Post content             |
| status   | choice | Yes      | 10         | draft, published, archived, deleted | Post status              |
| slug     | string | No       | 50         | -                                   | Auto-generated from title |

**Request Example:**

```bash
curl -k -L 'https://localhost/api/v1/posts/'
```

**Response Example:**

```json
{
    "data": [
        {
            "type": "posts",
            "id": "1",
            "attributes": {
                "title": "<post_title>",
                "slug": "<post_slug>",
                "content": "<post_content>",
                "status": "<post_status>",
                "created_at": "<datetime_object>",
                "updated_at": "<datetime_object>"
            },
            "relationships": {
                "author": {
                    "data": {
                        "type": "users",
                        "id": "1"
                    }
                },
                "category": {
                    "data": {
                        "type": "categories",
                        "id": "1"
                    }
                },
                "tags": {
                  "data": [
                    {
                      "type": "tags",
                      "id": "1"
                    },
                    {
                      "type": "tags",
                      "id": "2"
                    }
                  ]
                },
                "statistics": {
                    "data": {
                        "type": "post-statistics",
                        "id": "1"
                    }
                },
                "media_files": {
                    "data": [
                        {
                            "type": "media_files",
                            "id": "1"
                        },
                        {
                            "type": "media_files",
                            "id": "2"
                        }
                    ]
                }
            }
        },
    ]
}

```

#### Retrieve posts

**Method:** `GET`

**Endpoint:** `/api/v1/posts/<post_slug>/`

**Authentication:**

- None for posts with public status
- Admin or author for posts with private status

**Request Example:**

```bash
curl -k -L 'https://localhost/api/v1/posts/<post_slug>/'
```

**Response Example:**

```json
{
    "data": {
        "type": "posts",
            "id": "1",
            "attributes": {
                "title": "<post_title>",
                "slug": "<post_slug>",
                "content": "<post_content>",
                "status": "<post_status>",
                "created_at": "<datetime_object>",
                "updated_at": "<datetime_object>"
            },
        "relationships": {
            "author": {
                "data": {
                    "type": "users",
                    "id": "1"
                }
            },
            "category": {
                "data": {
                    "type": "categories",
                    "id": "1"
                }
            },
            "tags": {
                "data": [
                  {
                    "type": "tags",
                    "id": "1"
                  },
                  {
                    "type": "tags",
                    "id": "2"
                  }
                ]
              },
            "statistics": {
                "data": {
                    "type": "post-statistics",
                    "id": "1"
                }
            },
            "media_files": {
                "data": [
                    {
                        "type": "media_files",
                        "id": "1"
                    },
                    {
                        "type": "media_files",
                        "id": "2"
                    }
                ]
            }
        }
    },
    "included": [
        {
            "type": "users",
            "id": "1",
            "attributes": {
                "username": "<user_name>",
                "role": "<user_role>"
            }
        },
        {
            "type": "categories",
            "id": "1",
            "attributes": {
                "name": "<category_name>",
                "slug": "<category_slug>",
                "description": "<category_description>",
                "created_at": "<datetime_object>",
                "updated_at": "<datetime_object>"
            }
        },
        {
          "type": "tags",
          "id": "1",
          "attributes": {
            "name": "<tag_name>",
            "slug": "<tag_slug>",
            "created_at":"<datetime_object>",
            "updated_at":"<datetime_object>"
          }
        },
        {
          "type": "tags",
          "id": "2",
          "attributes": {
            "name": "<tag_name>",
            "slug": "<tag_slug>",
            "created_at":"<datetime_object>",
            "updated_at":"<datetime_object>"
          }
        },
        {
            "type": "post-statistics",
            "id": "1",
            "attributes": {
                "share_count": 0,
                "like_count": 0,
                "comment_count": 0,
                "created_at": "<datetime_object>",
                "updated_at": "<datetime_object>"
            }
        },
        {
            "type": "media_files",
            "id": "1",
            "attributes": {
                "file": "<file_path>",
                "type": "<file_type>",
                "created_at": "<datetime_object>",
                "updated_at": "<datetime_object>"
            }
        },
        {
            "type": "media_files",
            "id": "2",
            "attributes": {
                "file": "<file_path>",
                "type": "<file_type>",
                "created_at": "<datetime_object>",
                "updated_at": "<datetime_object>"
            }
        }
    ]
}
```

#### Create posts

**Method:** `POST`

**Endpoint:** `/api/v1/posts/`

**Authentication:** admin or author

**Request Example:**

```bash
curl -k -X POST \
  -L 'https://localhost/api/v1/posts/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -d '{
    "title": "<post_title>",
    "content": "<post_content>",
    "status": "<post_status>",
    "category": "<post_category_slug>"
  }'
```

Note: `title`, `status` and `category` fields are mandatory, otherwise it will launch 400 exception.

**Response Example:**

```json
{
    "data": {
        "type": "posts",
        "id": "1",
        "attributes": {
            "title": "<post_title>",
            "slug": "<post_slug>",
            "content": "<post_content>",
            "status": "draft",
            "created_at": "<datetime_object>",
            "updated_at": "<datetime_object>"
        },
        "relationships": {
            "author": {
                "data": {
                    "type": "users",
                    "id": "1"
                }
            },
            "category": {
                "data": {
                    "type": "categories",
                    "id": "1"
                }
            },
            "statistics": {
                "data": {
                    "type": "post-statistics",
                    "id": "1"
                }
            }
        }
    },
    "included": [
        {
            "type": "users",
            "id": "1",
            "attributes": {
                "username": "<user_name>",
                "role": "<user_role>"
            }
        },
        {
            "type": "categories",
            "id": "1",
            "attributes": {
                "name": "<category_name>",
                "description": "<category_description>",
                "slug": "<category_slug>",
                "created_at": "<datetime_object>",
                "updated_at": "<datetime_object>"
            }
        },
        {
            "type": "post-statistics",
            "id": "1",
            "attributes": {
                "share_count": 0,
                "like_count": 0,
                "comment_count": 0,
                "created_at": "<datetime_object>",
                "updated_at": "<datetime_object>"
            }
        }
    ]
}
```

Note: `title` and `category` fields are mandatory, otherwise it will launch 400 exception.

Note #2: by default, post status are set to `draft`, this ensures that content is not immediately visible to the public or regular users.

**Common errors:**

- **400 Bad Request:** Missing required fields.
- **403 Forbidden:** Not authenticated or not the author.

```json
{
  "errors": [
    {
      "status": "403",
      "title": "Forbidden",
      "detail": "You do not have permission to create posts.",
      "meta": {}
    }
  ]
}
```

#### Update posts

**Method:** `PATCH`

**Endpoint:** `/api/v1/posts/<post_slug>/`

**Authentication:** admin or own author

**Request Example:**

```bash
curl -k -X PATCH \
  -L 'https://localhost/api/v1/posts/<post_slug>/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -d '{
    "title": "<post_title>",
    "content": "<post_content>",
    "status": "<post_status>",
    "category": "<post_category_slug>"
  }'
```

**Response Example:**

```json
{
    "data": {
        "type": "posts",
        "id": "1",
        "attributes": {
            "title": "<post_title>",
            "slug": "<post_slug>",
            "content": "<post_content>",
            "status": "draft",
            "created_at": "<datetime_object>",
            "updated_at": "<datetime_object>"
        },
        "relationships": {
            "author": {
                "data": {
                    "type": "users",
                    "id": "1"
                }
            },
            "category": {
                "data": {
                    "type": "categories",
                    "id": "1"
                }
            },
            "statistics": {
                "data": {
                    "type": "post-statistics",
                    "id": "1"
                }
            }
        }
    },
    "included": [
        {
            "type": "users",
            "id": "1",
            "attributes": {
                "username": "<user_name>",
                "role": "<user_role>"
            }
        },
        {
            "type": "categories",
            "id": "1",
            "attributes": {
                "name": "<category_name>",
                "description": "<category_description>",
                "slug": "<category_slug>",
                "created_at": "<datetime_object>",
                "updated_at": "<datetime_object>"
            }
        },
        {
            "type": "post-statistics",
            "id": "1",
            "attributes": {
                "share_count": 0,
                "like_count": 0,
                "comment_count": 0,
                "created_at": "<datetime_object>",
                "updated_at": "<datetime_object>"
            }
        }
    ]
}
```

#### Delete posts

**Method:** `DELETE`

**Endpoint:** `/api/v1/posts/<post_slug>/`

**Authentication:** admin

**Request Example:**

```bash
curl -k -X DELETE \
  -L 'https://localhost/api/v1/posts/<post_slug>/' \
  -c cookies.txt -b cookies.txt \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFToken: <csrf_token>' \
  -H 'Origin: https://localhost' \
  -H 'Referer: https://localhost'
```

**Response Example:**

```http
204 No Content
```
