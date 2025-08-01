# FlatFund API - Floor Implementation Examples

## 🔄 Complete API Flow Examples with Floor Information

### 1. Invite Flatmate with Floor Information

**Request:**
```http
POST /invite-flatmate
Content-Type: application/json

{
  "apt_id": "PRESTIGE_HEIGHTS", 
  "flat_number": "204",
  "floor": "2",
  "owner_email_id": "owner@prestigeheights.com"
}
```

**Response:**
```json
{
  "status": true,
  "message": "Invitation sent successfully! The flatmate will receive an email with a 6-character invitation code.",
  "data": {
    "invitation_code": "XYZ789",
    "apartment_name": "Prestige Heights",
    "flat_number": "204", 
    "floor": "2",
    "invited_email": "owner@prestigeheights.com",
    "expires_in_days": 7,
    "invitation_uuid": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

### 2. Flatmate Signup with Floor Inheritance

**Request:**
```http
POST /signup
Content-Type: application/json

{
  "apartment_name": "Prestige Heights",
  "apt_id": "PRESTIGE_HEIGHTS",
  "flat_number": "204",
  "email_id": "newresident@example.com", 
  "unique_code": "XYZ789"
}
```

**Response:**
```json
{
  "status": true,
  "message": "🎉 Successfully registered! You are now added to Prestige Heights - Flat 204 as Tenant. Please proceed to login.",
  "data": {
    "user_id": "user_123",
    "flat_id": "tenant_PRESTIGE_HEIGHTS_204",
    "flat_uuid": "456e7890-e12b-34d5-a678-567890123456",
    "apartment_id": "PRESTIGE_HEIGHTS",
    "apartment_uuid": "789e0123-e45b-67d8-a901-234567890123",
    "apartment_name": "Prestige Heights",
    "flat_number": "204",
    "flat_floor": "2",
    "role": "tenant",
    "email": "newresident@example.com",
    "registration_date": "2025-08-01T12:00:00.000Z"
  }
}
```

### 3. Get User Apartments with Floor Information

**Request:**
```http
POST /get-apartments
Content-Type: application/json

{
  "email_id": "user@example.com"
}
```

**Response:**
```json
{
  "status": true,
  "message": "Apartments found for user",
  "apartments": [
    {
      "apartment_id": "PRESTIGE_HEIGHTS",
      "apartment_name": "Prestige Heights",
      "apartment_address": "123 MG Road, Bangalore",
      "flat_number": "204",
      "flat_floor": "2",
      "role": "tenant"
    },
    {
      "apartment_id": "BRIGADE_TOWERS",
      "apartment_name": "Brigade Towers", 
      "apartment_address": "456 Brigade Road, Bangalore",
      "flat_number": "G01",
      "flat_floor": "G",
      "role": "owner"
    }
  ]
}
```

### 4. Login with Floor Context

**Request:**
```http
POST /login
Content-Type: application/json

{
  "apt_id": "PRESTIGE_HEIGHTS",
  "email_id": "user@example.com"
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

**Email Content (HTML):**
```html
<div class="user-info">
  <div class="apartment-name">🏠 Prestige Heights</div>
  <div class="user-details">
    📍 Flat: 204 (Floor: 2) | 👤 Role: Tenant
  </div>
</div>
<div class="otp-container">
  <div class="otp-label">Your Login Code</div>
  <div class="otp-code">ABC123</div>
</div>
```

## 🇮🇳 Indian Floor Convention Examples

### Basement Floor
```json
{
  "floor": "B",
  "flat_number": "B01",
  "description": "Basement level flat"
}
```

### Ground Floor  
```json
{
  "floor": "G", 
  "flat_number": "G02",
  "description": "Ground floor flat (Indian standard)"
}
```

### Numbered Floors
```json
{
  "floor": "1",
  "flat_number": "101", 
  "description": "First floor flat"
}
```

```json
{
  "floor": "10",
  "flat_number": "1004",
  "description": "Tenth floor flat"
}
```

### Special Designations
```json
{
  "floor": "M",
  "flat_number": "M01",
  "description": "Mezzanine floor flat"
}
```

```json
{
  "floor": "UG",
  "flat_number": "UG03", 
  "description": "Upper Ground floor flat"
}
```

## 📧 Email Template Examples with Floor Context

### 1. Invitation Email
```html
<div class="apartment-info">
  <div class="apartment-name">🏠 Prestige Heights</div>
  <div class="flat-info">📍 Flat Number: 204 (Floor: 2)</div>
</div>
<div class="code-container">
  <div class="code-label">Your Invitation Code</div>
  <div class="invitation-code">XYZ789</div>
</div>
```

### 2. Welcome Email
```html
<div class="registration-info">
  <div class="apartment-name">🏠 Prestige Heights</div>
  <div class="details">📍 <strong>Flat:</strong> 204 (Floor: 2)</div>
  <div class="details">📧 <strong>Email:</strong> user@example.com</div>
  <div class="role-badge">Tenant</div>
</div>
```

### 3. Login OTP Email
```html
<div class="user-info">
  <div class="apartment-name">🏠 Prestige Heights</div>
  <div class="user-details">
    📍 Flat: 204 (Floor: 2) | 👤 Role: Tenant
  </div>
</div>
```

## 🎯 Floor Implementation Benefits

### For Users
- **Clear Identification**: Floor context in all communications
- **Familiar Conventions**: Standard Indian floor naming (B, G, 1, 2)
- **Better Navigation**: Easy flat location identification
- **Professional Emails**: Complete address information

### For Developers
- **Type Safety**: String-based floor field supports all conventions
- **API Consistency**: Floor information in all relevant responses
- **Backward Compatible**: Automatic migration from integer floors
- **Comprehensive Testing**: Full test coverage for floor functionality

### For Apartments
- **Organized Management**: Floor-based flat organization
- **Clear Communication**: Unambiguous flat identification
- **Scalable Design**: Supports buildings of any height
- **Indian Standards**: Native support for local conventions

## 🔧 Implementation Details

### Database Schema
```sql
-- Invitation table with floor support
CREATE TABLE flatmate_invitations (
  id INTEGER PRIMARY KEY,
  -- ... other fields ...
  floor TEXT,  -- Supports B, G, 1, 2, etc.
  -- ... other fields ...
);

-- User table with floor information
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  -- ... other fields ... 
  flat_floor TEXT,  -- Inherited from invitation
  -- ... other fields ...
);
```

### API Response Format
All responses include floor context where relevant:
```json
{
  "flat_number": "204",
  "flat_floor": "2",
  "apartment_name": "Prestige Heights"
}
```

### Email Integration
Floor context automatically included in:
- Invitation emails: `"Flat 204 (Floor: 2)"`
- Welcome emails: Complete flat details with floor
- Login emails: Floor context for identification
- All system notifications

---

**Implementation Status: ✅ Complete and Production Ready**

These examples demonstrate the comprehensive floor field support now available throughout the FlatFund API system.
