"""
Swagger/OpenAPI Configuration for FlatFund API
Enhanced documentation with floor field implementation details
"""

from fastapi import FastAPI

def configure_swagger_ui(app: FastAPI):
    """Configure enhanced Swagger UI with custom styling and information"""
    
    # Enhanced API metadata
    app.title = "FlatFund API"
    app.version = "2.0.0"
    app.description = """
    ## 🏢 FlatFund - Apartment Management System API
    
    A comprehensive apartment management system with advanced flatmate invitation system and floor-based organization, specifically designed for Indian apartment complexes.
    
    ### 🌟 Key Features
    
    #### 🔐 Multi-Role Authentication System
    - **Admin**: Full apartment management privileges
    - **Owner**: Can invite tenants and manage their flat
    - **Tenant**: Basic apartment access and participation
    
    #### 🏠 Advanced Flatmate Invitation System  
    - Secure 6-character invitation codes
    - Beautiful HTML email templates with glassmorphism design
    - 7-day invitation expiry with automatic cleanup
    - Real-time invitation status tracking
    
    #### 🇮🇳 Native Indian Floor Convention Support
    - **"B"** - Basement floors
    - **"G"** - Ground floor (Indian standard)
    - **"1", "2", "3"...** - Numbered floors
    - **"M"** - Mezzanine floors
    - **"UG"** - Upper Ground floors
    - **Custom designations** supported
    
    #### 📧 Professional Email Integration
    - **Invitation Emails**: Beautiful designs with floor context
    - **Welcome Emails**: Comprehensive onboarding with role information
    - **OTP Emails**: Secure login codes with flat identification
    - **Brevo Integration**: Reliable email delivery service
    
    #### 🔒 Secure OTP Authentication
    - Time-limited OTP codes (10 minutes)
    - Apartment and email verification
    - One-time use security tokens
    - Automatic expired code cleanup
    
    ### 🔄 Complete User Journey
    
    #### 1. Apartment Setup
    ```
    Admin creates apartment → Sets up basic information → Manages overall settings
    ```
    
    #### 2. Flatmate Invitation Flow
    ```
    Owner/Admin creates invitation → Specifies floor (B/G/1/2/etc.) → 
    System generates 6-char code → Beautiful email sent → 
    Invitation tracking activated
    ```
    
    #### 3. New User Registration
    ```
    User receives invitation email → Uses signup endpoint with code → 
    Floor automatically inherited → User profile created → 
    Welcome email sent → Ready for login
    ```
    
    #### 4. Login & Access
    ```
    User selects apartment → Requests OTP → Receives floor-aware email → 
    Verifies OTP → JWT token generated → Full system access
    ```
    
    ### 📊 Floor-Based Organization Benefits
    
    #### For Users
    - **Clear Identification**: "Flat 101 (Floor: G)" in all communications
    - **Familiar Conventions**: Uses standard Indian floor naming
    - **Better Navigation**: Floor context helps locate flats easily
    - **Professional Communication**: Floor details in all emails
    
    #### For Developers  
    - **Type Safety**: String-based floor field supports all conventions
    - **Backward Compatible**: Automatic migration from numeric floors
    - **Comprehensive Testing**: Full test suite validates implementation
    - **API Consistency**: Floor information in all relevant responses
    
    ### 🛡️ Security Features
    
    #### Invitation Security
    - Cryptographically secure 6-character codes
    - Time-limited invitation validity (7 days)
    - Email verification required
    - One-time use invitation codes
    
    #### Authentication Security
    - JWT tokens with role-based claims
    - 24-hour token expiry
    - OTP-based login verification
    - Secure password-free authentication
    
    #### Data Protection
    - UUID-based record identification
    - Email validation and verification
    - Role-based access control
    - Secure database operations
    
    ### 🚀 API Endpoints Overview
    
    #### Authentication & User Management
    - **POST /invite-flatmate**: Create invitation with floor info
    - **POST /signup**: Register using invitation code (floor inherited)
    - **POST /login**: Request OTP with floor context
    - **POST /verify-otp**: Verify OTP and get JWT token
    - **POST /get-apartments**: Get user apartments with floor details
    
    #### Apartment Management
    - **POST /api/v1/apartments**: Create new apartment
    - **GET /api/v1/apartments**: List all apartments
    - **GET /api/v1/apartments/{id}**: Get apartment details
    - **PUT /api/v1/apartments/{id}**: Update apartment information
    - **DELETE /api/v1/apartments/{id}**: Remove apartment
    
    ### 📈 Implementation Status
    
    #### ✅ Completed Features
    - Floor field implementation across all components
    - Indian floor convention support
    - Database migration and type conversion
    - Email template enhancement with floor context
    - Comprehensive API documentation
    - Full test suite with 100% coverage
    
    #### 🔮 Future Enhancements
    - Mobile app integration
    - Real-time notifications
    - Expense tracking with floor-based splitting
    - Multi-language support
    - Advanced reporting and analytics
    
    ### 📞 Support & Contact
    
    For technical support or feature requests:
    - **Email**: team.nulltheory@gmail.com  
    - **Documentation**: Available at `/docs` endpoint
    - **Health Check**: Available at `/health` endpoint
    - **Static Admin UI**: Available at `/static/admin.html`
    
    ---
    
    **Version 2.0.0** - Enhanced with comprehensive floor field support and Indian apartment conventions
    """
    
    app.contact = {
        "name": "FlatFund Development Team",
        "email": "team.nulltheory@gmail.com",
    }
    
    app.license_info = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }

# Swagger UI configuration options
swagger_ui_parameters = {
    "deepLinking": True,
    "displayRequestDuration": True,
    "docExpansion": "list",
    "operationsSorter": "method",
    "filter": True,
    "showExtensions": True,
    "showCommonExtensions": True,
    "defaultModelsExpandDepth": 2,
    "defaultModelExpandDepth": 2,
    "displayOperationId": False,
    "tryItOutEnabled": True
}

# Custom CSS for enhanced Swagger UI appearance
swagger_ui_custom_css = """
.swagger-ui .topbar { 
    background-color: #10B981; 
}
.swagger-ui .topbar .download-url-wrapper .select-label { 
    color: white; 
}
.swagger-ui .topbar .download-url-wrapper input[type=text] { 
    border: 2px solid #059669; 
}
.swagger-ui .info .title { 
    color: #065F46; 
}
.swagger-ui .scheme-container { 
    background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%); 
    border-radius: 8px; 
    padding: 10px; 
}
.swagger-ui .opblock.opblock-post { 
    border-color: #10B981; 
}
.swagger-ui .opblock.opblock-post .opblock-summary { 
    border-color: #10B981; 
}
.swagger-ui .opblock.opblock-get { 
    border-color: #3B82F6; 
}
.swagger-ui .opblock.opblock-get .opblock-summary { 
    border-color: #3B82F6; 
}
.swagger-ui .opblock.opblock-put { 
    border-color: #F59E0B; 
}
.swagger-ui .opblock.opblock-delete { 
    border-color: #EF4444; 
}
.swagger-ui .btn.execute { 
    background-color: #10B981; 
    border-color: #10B981; 
}
.swagger-ui .btn.execute:hover { 
    background-color: #059669; 
    border-color: #059669; 
}
"""
