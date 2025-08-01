# OTP Authentication System Documentation

## Overview
This document explains how to use the OTP (One-Time Password) authentication system for the FlatFund apartment management application.

## Prerequisites
1. **Brevo API Key**: You need to set up a Brevo (formerly SendinBlue) account and get an API key
   - Go to https://app.brevo.com/settings/keys/api
   - Create a new API key
   - Add it to your `.env` file as `BREVO_API_KEY=your-api-key-here`

2. **Environment Variables**: Make sure your `.env` file contains:
   ```
   SECRET_KEY=your-super-secret-jwt-key-change-in-production
   BREVO_API_KEY=your-brevo-api-key-here
   ```

## API Endpoints

### 1. Send OTP - `/api/v1/signin`
Sends a 4-digit OTP to the admin email for apartment authentication.

**Method**: `POST`
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "apt_id": "TESAPA",
  "admin_email": "admin@test.com"
}
```

**Success Response** (200):
```json
{
  "status": true,
  "message": "OTP sent successfully to your email",
  "expires_in_minutes": 10
}
```

**Error Responses**:
- `404`: Apartment not found or email doesn't match
- `500`: Email service configuration error

### 2. Verify OTP - `/api/v1/verify-otp`
Verifies the OTP and returns an authentication token with user details.

**Method**: `POST`
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "apt_id": "TESAPA",
  "admin_email": "admin@test.com",
  "otp": "1234"
}
```

**Success Response** (200):
```json
{
  "status": true,
  "message": "OTP verified successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "data": {
    "apt_id": "TESAPA",
    "apt_uuid": "b262e936-087f-4f97-8b40-029482fc5f9f",
    "flat_id": "admin_TESAPA",
    "flat_uuid": "c123d456-789e-0fgh-ijkl-123456789012",
    "user_id": "user_1",
    "is_all_user_details_filled": false,
    "role": "admin"
  }
}
```

**Error Responses**:
- `400`: Invalid or expired OTP
- `404`: Apartment not found or email doesn't match

## Authentication Flow

1. **Admin requests OTP**: Send apartment ID and admin email to `/api/v1/signin`
2. **System validates**: Checks if apartment exists and email matches
3. **OTP generated**: 4-digit OTP is generated and stored with 10-minute expiry
4. **Email sent**: OTP is sent to admin email via Brevo
5. **Admin verifies**: Admin enters OTP and submits to `/api/v1/verify-otp`
6. **Token issued**: System validates OTP and returns JWT token with user data

## Database Tables

### Users Table
| Column Name         | Data Type | Notes                    |
| ------------------- | --------- | ------------------------ |
| id                  | int       | Primary Key              |
| flat_uuid           | uuid      | Unique identifier        |
| flat_id             | string    | Flat identifier          |
| apartment_uuid      | uuid      | Reference to apartment   |
| apartment_id        | string    | Reference to apartment   |
| user_name           | string    | User's full name         |
| user_phone_number   | string    | Phone number             |
| user_email_id       | string    | Email address            |
| flat_number         | string    | Flat/unit number         |
| flat_floor          | int       | Floor number             |
| role                | enum      | admin/tenant/owner       |
| created_at          | timestamp | Record creation time     |
| updated_at          | timestamp | Last update time         |

### OTP Verifications Table
| Column Name  | Data Type | Notes                    |
| ------------ | --------- | ------------------------ |
| id           | int       | Primary Key              |
| email        | string    | Email address            |
| apartment_id | string    | Apartment identifier     |
| otp_code     | string    | 4-digit OTP code         |
| is_verified  | int       | 0=Not verified, 1=Verified |
| expires_at   | timestamp | OTP expiration time      |
| created_at   | timestamp | Record creation time     |

## JWT Token Structure

The JWT token contains the following claims:
```json
{
  "user_id": "1",
  "apt_id": "TESAPA",
  "apt_uuid": "b262e936-087f-4f97-8b40-029482fc5f9f",
  "role": "admin",
  "email": "admin@test.com",
  "exp": 1234567890
}
```

## Testing the System

### 1. Create a Test Apartment
```bash
curl -X POST "http://localhost:8001/api/v1/apartments/" \
-H "Content-Type: application/json" \
-d '{
  "apartment_name": "Test Apartment",
  "apartment_address": "123 Test Street",
  "admin_email": "your-email@test.com",
  "total_floors": 5,
  "total_flats": 20,
  "water_bill_mode": 0
}'
```

### 2. Request OTP
```bash
curl -X POST "http://localhost:8001/api/v1/signin" \
-H "Content-Type: application/json" \
-d '{
  "apt_id": "TESAPA",
  "admin_email": "your-email@test.com"
}'
```

### 3. Verify OTP
```bash
curl -X POST "http://localhost:8001/api/v1/verify-otp" \
-H "Content-Type: application/json" \
-d '{
  "apt_id": "TESAPA",
  "admin_email": "your-email@test.com",
  "otp": "1234"
}'
```

## Security Features

1. **OTP Expiry**: OTPs expire after 10 minutes
2. **Single Use**: Each OTP can only be used once
3. **Email Validation**: OTP is sent only to registered admin email
4. **JWT Tokens**: Secure token-based authentication
5. **Apartment Validation**: System validates apartment existence before sending OTP

## Error Handling

- **Invalid Email**: System validates email format
- **Apartment Not Found**: Returns 404 if apartment doesn't exist
- **Email Mismatch**: Returns 404 if email doesn't match apartment admin
- **Expired OTP**: Returns 400 if OTP is expired
- **Invalid OTP**: Returns 400 if OTP is incorrect
- **Email Service Error**: Returns 500 if email sending fails

## Rate Limiting (Recommended)

For production, consider implementing rate limiting to prevent OTP abuse:
- Maximum 3 OTP requests per email per hour
- Maximum 5 verification attempts per OTP
- Block IP after multiple failed attempts

## Production Deployment

1. **Environment Variables**: 
   - Set strong `SECRET_KEY`
   - Configure `BREVO_API_KEY`
   - Set `USE_LOCAL_DB=false` for PostgreSQL

2. **Database**: 
   - Use PostgreSQL in production
   - Set up proper database backups
   - Configure connection pooling

3. **Security**:
   - Use HTTPS in production
   - Configure CORS properly
   - Set up proper logging
   - Monitor OTP usage patterns
