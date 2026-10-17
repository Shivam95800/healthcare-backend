# Healthcare Backend API

Production-style Django REST Framework backend built with PostgreSQL (using Django ORM), JWT Authentication (`djangorestframework-simplejwt`), and environment configuration via `django-environ`.

---

## Architecture & Features

- **Custom User Model**: Uses `email` as the unique `USERNAME_FIELD` (case-insensitive login, name field, hashed passwords).
- **Ownership Isolation**:
  - `Patient` records are strictly tied to `created_by` (FK to User).
  - A user cannot read, update, or delete patients created by other users (returns 404).
- **Exact Mapping Routes (Spec Compliant)**:
  - `POST /api/mappings/`: Assigns a doctor to a patient. Only patients owned by the requesting user can be assigned. Duplicate mappings are rejected with clear error messages.
  - `GET /api/mappings/<patient_id>/`: Lists all doctors assigned to that patient (patient must belong to requesting user).
  - `DELETE /api/mappings/<id>/`: Removes a mapping by its mapping ID (mapping must belong to a patient owned by requesting user).
  - *Both routes share the `/api/mappings/<identifier>/` endpoint and are dispatched by HTTP method.*
- **Custom Exception Handler**: Standardized error responses returning `{ "success": false, "status_code": ..., "message": ..., "errors": ... }`.
- **Validation**:
  - Patient age must be between 1 and 149 (`0 < age < 150`).
  - Doctor experience must be `>= 0`.
  - Non-existent IDs return structured 404 or validation errors.

---

## Directory Structure

```text
healthcare_backend/
├── .env.example
├── .gitignore
├── requirements.txt
├── manage.py
├── README.md
├── healthcare_backend/
│   ├── __init__.py
│   ├── asgi.py
│   ├── exceptions.py
│   ├── permissions.py
│   ├── settings.py
│   ├── settings_test.py
│   ├── urls.py
│   └── wsgi.py
├── users/
│   ├── admin.py, apps.py, managers.py, models.py, serializers.py, tests.py, urls.py, views.py
├── patients/
│   ├── admin.py, apps.py, models.py, serializers.py, tests.py, urls.py, views.py
├── doctors/
│   ├── admin.py, apps.py, models.py, serializers.py, tests.py, urls.py, views.py
└── mappings/
    ├── admin.py, apps.py, models.py, serializers.py, tests.py, urls.py, views.py
```

---

## Setup & Execution

### 1. Environment & Virtualenv Setup

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. PostgreSQL Setup

1. Start your local PostgreSQL server or container.
2. Create the database and user:
   ```sql
   CREATE DATABASE healthcare_db;
   CREATE USER postgres WITH ENCRYPTED PASSWORD 'postgres';
   GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO postgres;
   \c healthcare_db
   GRANT ALL ON SCHEMA public TO postgres;
   ```
3. Copy `.env.example` to `.env` and verify database credentials:
   ```bash
   cp .env.example .env
   ```

### 3. Apply Migrations

```bash
# Generate migration files (already generated in workspace)
python manage.py makemigrations users patients doctors mappings

# Apply migrations to PostgreSQL
python manage.py migrate
```

### 4. Run Automated Tests

To run the automated tests against SQLite (or once PostgreSQL is running):
```bash
python manage.py test --settings=healthcare_backend.settings_test
```
*All 12 test cases cover registration, login, token issuance, patient ownership isolation, doctor creation, and duplicate mapping rejection.*

### 5. Start Development Server

```bash
python manage.py runserver
```

---

## API Documentation & Examples

All authenticated requests must include the header:
```text
Authorization: Bearer <access_token>
```

### 1. Authentication

#### Register: `POST /api/auth/register/` (Public)
Request:
```json
{
  "name": "Dr. Sarah Connor",
  "email": "sarah@example.com",
  "password": "StrongPassword123!",
  "password_confirm": "StrongPassword123!"
}
```
Response (`201 Created`):
```json
{
  "success": true,
  "message": "User registered successfully.",
  "data": {
    "id": 1,
    "name": "Dr. Sarah Connor",
    "email": "sarah@example.com",
    "created_at": "2026-10-17T07:00:00Z"
  }
}
```

#### Login: `POST /api/auth/login/` (Public)
Request:
```json
{
  "email": "sarah@example.com",
  "password": "StrongPassword123!"
}
```
Response (`200 OK`):
```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "user": {
      "id": 1,
      "name": "Dr. Sarah Connor",
      "email": "sarah@example.com",
      "created_at": "2026-10-17T07:00:00Z"
    },
    "access": "<jwt_access_token>",
    "refresh": "<jwt_refresh_token>"
  }
}
```

---

### 2. Patients (Scoped to Owner)

#### Create Patient: `POST /api/patients/`
Request:
```json
{
  "name": "John Doe",
  "age": 45,
  "gender": "M",
  "phone": "+1-555-0199",
  "address": "404 Elm St, Springfield",
  "medical_history": "Mild hypertension, penicillin allergy"
}
```
Response (`201 Created`):
```json
{
  "id": 1,
  "name": "John Doe",
  "age": 45,
  "gender": "M",
  "phone": "+1-555-0199",
  "address": "404 Elm St, Springfield",
  "medical_history": "Mild hypertension, penicillin allergy",
  "created_by": "sarah@example.com",
  "created_at": "2026-10-17T07:05:00Z",
  "updated_at": "2026-10-17T07:05:00Z"
}
```

#### List Patients: `GET /api/patients/`
Returns only patients created by the authenticated user.

#### Retrieve / Update / Delete Patient: `/api/patients/<id>/`
- `GET /api/patients/1/`
- `PUT /api/patients/1/`
- `DELETE /api/patients/1/`
*Accessing a patient created by another user returns `404 Not Found`.*

---

### 3. Doctors

#### Create Doctor: `POST /api/doctors/`
Request:
```json
{
  "name": "Gregory House",
  "specialization": "Diagnostic Medicine",
  "email": "house@princetonplainsboro.org",
  "phone": "+1-555-0143",
  "years_of_experience": 20
}
```
Response (`201 Created`):
```json
{
  "id": 1,
  "name": "Gregory House",
  "specialization": "Diagnostic Medicine",
  "email": "house@princetonplainsboro.org",
  "phone": "+1-555-0143",
  "years_of_experience": 20,
  "created_at": "2026-10-17T07:10:00Z",
  "updated_at": "2026-10-17T07:10:00Z"
}
```

#### List / Retrieve / Update / Delete Doctors
- `GET /api/doctors/`
- `GET /api/doctors/<id>/`
- `PUT /api/doctors/<id>/`
- `DELETE /api/doctors/<id>/`

---

### 4. Patient-Doctor Mappings

#### Assign Doctor to Patient: `POST /api/mappings/`
*(Patient must belong to requesting user; duplicates are rejected)*
Request:
```json
{
  "patient_id": 1,
  "doctor_id": 1
}
```
Response (`201 Created`):
```json
{
  "id": 1,
  "patient": {
    "id": 1,
    "name": "John Doe",
    "age": 45,
    "gender": "M",
    "phone": "+1-555-0199",
    "address": "404 Elm St, Springfield",
    "medical_history": "Mild hypertension, penicillin allergy",
    "created_by": "sarah@example.com",
    "created_at": "2026-10-17T07:05:00Z",
    "updated_at": "2026-10-17T07:05:00Z"
  },
  "doctor": {
    "id": 1,
    "name": "Gregory House",
    "specialization": "Diagnostic Medicine",
    "email": "house@princetonplainsboro.org",
    "phone": "+1-555-0143",
    "years_of_experience": 20,
    "created_at": "2026-10-17T07:10:00Z",
    "updated_at": "2026-10-17T07:10:00Z"
  },
  "created_at": "2026-10-17T07:15:00Z"
}
```

#### List All Mappings for Owner: `GET /api/mappings/`
Returns all mappings associated with patients owned by the requesting user.

#### List Doctors for a Specific Patient: `GET /api/mappings/<patient_id>/`
Response (`200 OK`):
```json
{
  "patient_id": 1,
  "patient_name": "John Doe",
  "assigned_doctors_count": 1,
  "doctors": [
    {
      "id": 1,
      "name": "Gregory House",
      "specialization": "Diagnostic Medicine",
      "email": "house@princetonplainsboro.org",
      "phone": "+1-555-0143",
      "years_of_experience": 20,
      "created_at": "2026-10-17T07:10:00Z",
      "updated_at": "2026-10-17T07:10:00Z"
    }
  ]
}
```

#### Delete Mapping: `DELETE /api/mappings/<id>/`
Response (`204 No Content`).
