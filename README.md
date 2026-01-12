# SaaS-Style Task Management Platform – Backend Documentation

## Overview
This project is a **production-grade, backend-first SaaS platform** built with a strong focus on **clean architecture**, **domain-driven design**, and **long-term maintainability**.

The backend is intentionally designed to be:
- Framework-aware but not framework-dependent
- Safe to refactor due to deep test coverage
- Ready for frontend integration
- Suitable as a real SaaS foundation

---

## Tech Stack

- **Backend Framework:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** Clerk (JWT via JWKS)
- **Containerization:** Docker + Docker Compose
- **Testing:** pytest + pytest-django

---

## Core Infrastructure

### BaseModel
All domain models inherit from `BaseModel`, which provides:
- UUID primary key
- `created` / `updated` timestamps
- Soft delete via `is_active` and `deleted_at`

Soft deletion is enforced across all selectors and services.

---

## Authentication & Authorization

### Authentication
- Uses **Clerk** for authentication
- JWT tokens verified using JWKS
- Custom DRF authentication class
- Automatic user creation on first login

### Authorization
- Object-level permissions
- Boolean-only permission classes
- Ownership enforced at selector and service layers

---

## Domain Models

### Project
- Single owner
- Soft deleted
- Owner-scoped name uniqueness
- Private by default

### Task
- Belongs to a project
- Optional assignee
- Ownership inherited from project
- Soft deleted

---

## Services Layer

Services encapsulate all **business rules**:

- Transactional writes
- Explicit exception handling
- No HTTP or DRF dependencies

Examples:
- `ProjectService.create_project`
- `TaskService.update_task`

---

## Selectors Layer

Selectors are:
- Read-only
- Exception-free
- Ownership-aware
- Soft-delete aware

They return querysets or `None`, never raising domain errors.

---

## Serializers

Serializers are explicit and purpose-specific:

### Project Serializers
- List serializer
- Detail serializer
- Write serializer

### Task Serializers
- List serializer
- Detail serializer
- Write serializer

No `ModelSerializer` magic is used.

---

## Pagination

Pagination is:
- Centralized
- Applied only to list endpoints
- Consistent across APIs

Metadata returned:
- page
- page_size
- total_pages
- total_items

---

## Rate Limiting

- Global user-based throttling enabled
- Default: `1000 requests/day` per authenticated user
- Implemented via DRF throttling
- Centralized configuration

---

## API Endpoints

### Projects
- `GET /api/v1/projects/`
- `POST /api/v1/projects/`
- `GET /api/v1/projects/{project_id}/`
- `PUT /api/v1/projects/{project_id}/`
- `DELETE /api/v1/projects/{project_id}/`

### Tasks
- `GET /api/v1/projects/{project_id}/tasks/`
- `POST /api/v1/projects/{project_id}/tasks/`
- `GET /api/v1/projects/{project_id}/tasks/{task_id}/`
- `PUT /api/v1/projects/{project_id}/tasks/{task_id}/`
- `DELETE /api/v1/projects/{project_id}/tasks/{task_id}/`

### Utility
- `GET /api/v1/tasks/assigned-to-me/`

---

## Testing Strategy

Testing follows a **test pyramid**:

- BaseModel tests
- Selector tests
- Service tests
- API tests

All critical layers are covered using pytest.







