# QAI API Documentation

Base URL: `http://localhost:3000` (or your deployed server URL)

## Results Endpoints

### Create New Result
**POST** `/results`

Creates a new test result entry for a PR.

**Request Body:**
```json
{
  "prLink": "https://github.com/user/repo/pull/123",
  "prName": "Feature: Add user authentication"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Result created successfully",
  "data": {
    "id": 1,
    "created_at": "2024-01-15T10:30:00.000Z",
    "pr-link": "https://github.com/user/repo/pull/123",
    "pr-name": "Feature: Add user authentication",
    "res-success": false
  }
}
```

### Update Result Success Status
**PATCH** `/results/:id`

Updates the overall success status of a test result.

**Request Body:**
```json
{
  "resSuccess": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Result updated successfully",
  "data": {
    "id": 1,
    "created_at": "2024-01-15T10:30:00.000Z",
    "pr-link": "https://github.com/user/repo/pull/123",
    "pr-name": "Feature: Add user authentication",
    "res-success": true
  }
}
```

### Get All Results
**GET** `/results`

Retrieves all test results, ordered by creation date (newest first).

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "created_at": "2024-01-15T10:30:00.000Z",
      "pr-link": "https://github.com/user/repo/pull/123",
      "pr-name": "Feature: Add user authentication",
      "res-success": true
    }
  ]
}
```

## Test Suites Endpoints

### Create New Test Suite
**POST** `/suites`

Creates a new test suite linked to a result.

**Request Body:**
```json
{
  "resultId": 1,
  "name": "Authentication Flow Tests",
  "s3Link": "https://bucket.s3.amazonaws.com/video_123.mp4",
  "suitesSuccess": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Suite created successfully",
  "data": {
    "id": 1,
    "created_at": "2024-01-15T10:35:00.000Z",
    "name": "Authentication Flow Tests",
    "s3-link": "https://bucket.s3.amazonaws.com/video_123.mp4",
    "suites-success": false
  }
}
```

### Update Test Suite
**PATCH** `/suites/:id`

Updates suite success status and/or S3 link.

**Request Body:**
```json
{
  "suitesSuccess": true,
  "s3Link": "https://bucket.s3.amazonaws.com/video_123_updated.mp4"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Suite updated successfully",
  "data": {
    "id": 1,
    "created_at": "2024-01-15T10:35:00.000Z",
    "name": "Authentication Flow Tests",
    "s3-link": "https://bucket.s3.amazonaws.com/video_123_updated.mp4",
    "suites-success": true
  }
}
```

### Get Suites for Result
**GET** `/results/:id/suites`

Retrieves all test suites for a specific result.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "created_at": "2024-01-15T10:35:00.000Z",
      "name": "Authentication Flow Tests",
      "s3-link": "https://bucket.s3.amazonaws.com/video_123.mp4",
      "suites-success": true
    }
  ]
}
```

## Individual Tests Endpoints

### Create New Test
**POST** `/tests`

Creates a new individual test linked to a suite.

**Request Body:**
```json
{
  "suiteId": 1,
  "name": "Login with valid credentials",
  "summary": "Test successful login flow with email and password",
  "testSuccess": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test created successfully",
  "data": {
    "id": 1,
    "created_at": "2024-01-15T10:40:00.000Z",
    "name": "Login with valid credentials",
    "summary": "Test successful login flow with email and password",
    "test-success": true
  }
}
```

### Update Test
**PATCH** `/tests/:id`

Updates test success status and/or summary.

**Request Body:**
```json
{
  "testSuccess": false,
  "summary": "Test failed due to timeout on login button click"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test updated successfully",
  "data": {
    "id": 1,
    "created_at": "2024-01-15T10:40:00.000Z",
    "name": "Login with valid credentials",
    "summary": "Test failed due to timeout on login button click",
    "test-success": false
  }
}
```

### Get Tests for Suite
**GET** `/suites/:id/tests`

Retrieves all individual tests for a specific suite.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "created_at": "2024-01-15T10:40:00.000Z",
      "name": "Login with valid credentials",
      "summary": "Test successful login flow with email and password",
      "test-success": true
    }
  ]
}
```

## Legacy Endpoints

### Upload Video to S3
**POST** `/upload-video`

Uploads a video file to S3 storage.

**Request:** Multipart form data with `video` field

**Response:**
```json
{
  "success": true,
  "message": "Video uploaded successfully",
  "fileUrl": "https://bucket.s3.amazonaws.com/video_1642248000000_test.mp4",
  "fileName": "video_1642248000000_test.mp4"
}
```

### Upload JSON Data
**POST** `/upload-data`

Uploads JSON data to Supabase table.

**Request Body:** Any JSON object

**Response:**
```json
{
  "success": true,
  "message": "Data uploaded successfully",
  "data": [...]
}
```

## Error Responses

All endpoints return error responses in this format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `400` - Bad Request (missing required fields)
- `500` - Internal Server Error (database/S3 errors)

## Database Schema

### Results Table
```sql
CREATE TABLE public.results (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  pr-link text,
  res-success boolean DEFAULT false,
  pr-name text,
  CONSTRAINT results_pkey PRIMARY KEY (id)
);
```

### Suites Table
```sql
CREATE TABLE public.suites (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  suites-success boolean,
  name text,
  s3-link text,
  CONSTRAINT suites_pkey PRIMARY KEY (id),
  CONSTRAINT suites_id_fkey FOREIGN KEY (id) REFERENCES public.results(id)
);
```

### Tests Table
```sql
CREATE TABLE public.tests (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  summary text,
  test-success boolean,
  name text,
  CONSTRAINT tests_pkey PRIMARY KEY (id),
  CONSTRAINT tests_id_fkey FOREIGN KEY (id) REFERENCES public.suites(id)
);
```

## Workflow Examples

### Upload Everything Before Agent Execution
1. `POST /results` - Create result entry
2. `POST /suites` - Create suite entries (with `suitesSuccess: false`)
3. `POST /tests` - Create test entries (with `testSuccess: false`)
4. Execute agents...
5. `PATCH /tests/:id` - Update individual test results
6. `PATCH /suites/:id` - Update suite results
7. `PATCH /results/:id` - Update overall result

### Upload After Agent Completion
1. Execute agents...
2. `POST /results` - Create result with final status
3. `POST /suites` - Create suites with final results
4. `POST /tests` - Create tests with final results