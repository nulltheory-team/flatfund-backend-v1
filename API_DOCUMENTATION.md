# FlatFund Backend API Documentation

## Overview
FlatFund is a comprehensive apartment management system that enables secure user registration, authentication, and flat management through a role-based system.

## Base URL
```
http://localhost:8000
```

## Authentication
- **JWT Token**: Required for protected endpoints
- **OTP Verification**: Email-based OTP system for secure login
- **Role-based Access**: ADMIN, OWNER, TENANT roles

---

## 🏢 Apartment Management

### Create Apartment
**Endpoint:** `POST /apartments/`

**Request Body:**
```json
{
  "apartment_name": "Green Acres Residency",
  "apartment_address": "123 Main Street, City",
  "admin_email": "admin@greenliving.com",
  "total_floors": 10,
  "total_flats": 40,
  "water_bill_mode": 0
}
```

**Response:**
```json
{
  "id": 1,
  "apartment_id": "GA001",
  "apartment_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "apartment_name": "Green Acres Residency",
  "apartment_address": "123 Main Street, City",
  "admin_email": "admin@greenliving.com",
  "total_floors": 10,
  "total_flats": 40,
  "water_bill_mode": 0,
  "created_at": "2025-07-31T12:00:00Z"
}
```

**Notes:**
- `water_bill_mode`: 0 = Meter based, 1 = Tanker based
- `apartment_id` is auto-generated
- Admin email becomes the apartment administrator

---

## 👥 Flatmate Invitation System

### 1. Invite Flatmate
**Endpoint:** `POST /api/v1/invite-flatmate`

**Description:** Admin invites new flatmates to join the apartment with a 6-character invitation code.

**Request Body:**
```json
{
  "apt_id": "GA001",
  "flat_number": "A-203",
  "owner_email_id": "john.doe@example.com"
}
```

**Response:**
```json
{
  "status": true,
  "message": "Flatmate invitation sent successfully",
  "data": {
    "invitation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "apartment_id": "GA001",
    "apartment_name": "Green Acres Residency",
    "flat_number": "A-203",
    "invited_email": "john.doe@example.com",
    "invitation_code": "ABC123",
    "expires_at": "2025-08-07T12:00:00Z",
    "expires_in_days": 7
  }
}
```

**Features:**
- Generates unique 6-character alphanumeric code
- Code expires in 7 days
- Sends beautiful email invitation
- Prevents duplicate invitations

---

### 2. Flatmate Signup
**Endpoint:** `POST /api/v1/signup`

**Description:** Secure signup process with comprehensive verification.

**Request Body:**
```json
{
  "apartment_name": "Green Acres Residency",
  "apt_id": "GA001",
  "flat_number": "A-203",
  "email_id": "john.doe@example.com",
  "unique_code": "ABC123"
}
```

**Response:**
```json
{
  "status": true,
  "message": "🎉 Successfully registered! You are now added to Green Acres Residency - Flat A-203 as Owner. Please proceed to login.",
  "data": {
    "user_id": "user_123",
    "flat_id": "owner_GA001_A-203",
    "flat_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "apartment_id": "GA001",
    "apartment_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "apartment_name": "Green Acres Residency",
    "flat_number": "A-203",
    "role": "owner",
    "email": "john.doe@example.com",
    "registration_date": "2025-07-31T12:00:00Z"
  }
}
```

**Security Features:**
- Verifies apartment name + ID match
- Checks invitation code validity and expiry
- Prevents duplicate registrations
- First user in flat becomes OWNER, subsequent users become TENANT

**Error Responses:**
```json
{
  "detail": "Invalid apartment details. Please check apartment name and ID."
}
```

```json
{
  "detail": "Your invitation code has expired. Please contact the apartment admin for a new invitation."
}
```

```json
{
  "detail": "This invitation code has already been used. If you need access, please contact the apartment admin."
}
```

---

## 🔐 Login System

### 1. Get User Apartments
**Endpoint:** `POST /api/v1/get-apartments`

**Description:** Retrieve list of apartments where user is registered.

**Request Body:**
```json
{
  "email_id": "john.doe@example.com"
}
```

**Response:**
```json
{
  "status": true,
  "message": "Apartments retrieved successfully",
  "apartments": [
    {
      "apartment_id": "GA001",
      "apartment_name": "Green Acres Residency",
      "apartment_address": "123 Main Street, City",
      "flat_number": "A-203",
      "role": "owner"
    },
    {
      "apartment_id": "BV002",
      "apartment_name": "Blue Valley Apartments",
      "apartment_address": "456 Oak Avenue, City",
      "flat_number": "B-101",
      "role": "tenant"
    }
  ]
}
```

---

### 2. Login with OTP
**Endpoint:** `POST /api/v1/login`

**Description:** User selects apartment and receives OTP for secure login.

**Request Body:**
```json
{
  "apt_id": "GA001",
  "email_id": "john.doe@example.com"
}
```

**Response:**
```json
{
  "status": true,
  "message": "OTP sent successfully to your email",
  "expires_in_minutes": 10
}
```

**Features:**
- Sends 4-digit OTP via email
- OTP expires in 10 minutes
- Beautiful email template with user info

---

## 🔑 OTP Authentication

### 1. Admin Signin (Legacy)
**Endpoint:** `POST /api/v1/signin`

**Description:** Original admin signin system (maintained for backward compatibility).

**Request Body:**
```json
{
  "apt_id": "GA001",
  "admin_email": "admin@greenliving.com"
}
```

**Response:**
```json
{
  "status": true,
  "message": "OTP sent successfully to your email",
  "expires_in_minutes": 10
}
```

---

### 2. Verify OTP
**Endpoint:** `POST /api/v1/verify-otp`

**Description:** Verify OTP and receive JWT authentication token.

**Request Body:**
```json
{
  "apt_id": "GA001",
  "admin_email": "admin@greenliving.com",
  "otp": "1234"
}
```

**Response:**
```json
{
  "status": true,
  "message": "OTP verified successfully",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "data": {
    "apt_id": "GA001",
    "apt_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "flat_id": "admin_GA001",
    "flat_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "user_id": "user_123",
    "is_all_user_details_filled": true,
    "role": "admin"
  }
}
```

**JWT Token Details:**
- **Algorithm:** HS256
- **Expiry:** 24 hours
- **Contains:** user_id, apt_id, apt_uuid, role, email

---

## 🏠 Tenant Management

### Assign Additional Tenant
**Endpoint:** `POST /api/v1/assign-additional-tenant`

**Description:** Direct tenant assignment to existing flat (no invitation process required).

**Request Body:**
```json
{
  "apt_id": "GA001",
  "flat_id": "tenant_GA001_A-203",
  "tenant_email_id": "tenant@example.com"
}
```

**Response:**
```json
{
  "status": true,
  "message": "Additional tenant assigned successfully to the flat",
  "data": {
    "tenant_user_id": "user_456",
    "flat_id": "tenant_GA001_A-203",
    "flat_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "tenant_email": "tenant@example.com",
    "apartment_id": "GA001",
    "role": "tenant"
  }
}
```

**Use Case:** For direct tenant assignments without the invitation code process.

---

## 👤 User Management

### Update User Role
**Endpoint:** `PUT /api/v1/user/{user_id}/role`

**Description:** Update user role (admin can change owner ↔ tenant, only admin email can be admin).

**Request Body:**
```json
{
  "new_role": "tenant"
}
```

**Response:**
```json
{
  "status": true,
  "message": "User role updated from owner to tenant",
  "user": {
    "user_id": 123,
    "email": "john.doe@example.com",
    "old_role": "owner",
    "new_role": "tenant",
    "flat_id": "tenant_GA001_A-203"
  }
}
```

**Security Rules:**
- Only admin role can be assigned to apartment admin email
- Admin email cannot be changed to non-admin role
- Supports role changes between owner ↔ tenant

---

## 📊 Data Models

### User Roles
- **ADMIN**: Apartment administrator (admin email only)
- **OWNER**: Primary flat resident (first person in flat)
- **TENANT**: Additional flat residents

### Flat ID Format
- **Admin**: `admin_{apartment_id}`
- **Owner**: `owner_{apartment_id}_{flat_number}`
- **Tenant**: `tenant_{apartment_id}_{flat_number}`

### Database Tables
- **apartments**: Apartment information
- **users**: User accounts and roles
- **otp_verifications**: OTP codes for authentication
- **flatmate_invitations**: Invitation codes and tracking

---

## 🔒 Security Features

### Invitation System Security
- ✅ Unique 6-character alphanumeric codes
- ✅ 7-day expiration
- ✅ One-time use only
- ✅ Email + apartment + flat verification
- ✅ Admin validation check

### Authentication Security
- ✅ JWT tokens with 24-hour expiry
- ✅ 4-digit OTP with 10-minute expiry
- ✅ Email-based verification
- ✅ Role-based access control
- ✅ Admin role protection

### Data Validation
- ✅ Comprehensive apartment verification
- ✅ Duplicate prevention
- ✅ Email format validation
- ✅ Cross-platform UUID support
- ✅ Secure error messages

---

## 📧 Email Templates

### Invitation Email
- **Subject:** "🏠 You're Invited to Join {apartment_name} on FlatFund!"
- **Features:** Modern glassmorphism design, animated gradients, responsive layout
- **Content:** Invitation code, apartment details, next steps

### Login OTP Email
- **Subject:** "🔐 Your FlatFund Login Code for {apartment_name}"
- **Features:** Secure design, user role display, expiry timer
- **Content:** 4-digit OTP, user details, security notes

### Welcome Email
- **Subject:** "🎉 Welcome to {apartment_name} - Registration Successful!"
- **Features:** Congratulatory design, role badge, next steps guide
- **Content:** Registration confirmation, user role, login instructions

---

## 🚀 Getting Started

### 1. Admin Setup
1. Create apartment using `POST /apartments/`
2. Admin can now use `POST /api/v1/signin` for legacy access

### 2. Invite Flatmates
1. Use `POST /api/v1/invite-flatmate` to send invitations
2. Flatmates receive email with 6-character code

### 3. Flatmate Registration
1. Use `POST /api/v1/signup` with all required details
2. First person becomes OWNER, others become TENANT

### 4. Login Flow
1. Use `POST /api/v1/get-apartments` to see available apartments
2. Use `POST /api/v1/login` to request OTP
3. Use `POST /api/v1/verify-otp` to get JWT token

---

## 📝 Notes

- All timestamps are in ISO 8601 format
- UUIDs are used for apartment and user identification
- SQLite for development, PostgreSQL for production
- Email service powered by Brevo API
- CORS enabled for frontend integration
- Comprehensive error handling and validation

---

## 🔧 Environment Variables

```env
SECRET_KEY=your-jwt-secret-key
BREVO_API_KEY=your-brevo-api-key
DATABASE_URL=sqlite:///./apartments.db  # or PostgreSQL URL
```

---

*Last updated: July 31, 2025*
