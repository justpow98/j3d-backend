# Backend Architecture

## Overview

The 3D Print Shop Manager backend is a Flask-based REST API designed to manage orders, inventory, and 3D printers (specifically Bambu Lab printers). It integrates with Etsy for order management and Bambu Connect for printer control.

## Technology Stack

- **Framework**: Flask 3.0.0
- **ORM**: SQLAlchemy 3.1.3
- **Database**: PostgreSQL 15
- **Authentication**: JWT (PyJWT 2.8.1)
- **HTTP Client**: Requests 2.31.0
- **Environment**: Python 3.10+

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                        │
│                    (Angular Frontend, Mobile, etc)               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      API Layer (Flask)                           │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────┐
│  │   Auth   │ Orders   │Filaments │ Printers │Analytics │Webhooks
│  │ Endpoints│Endpoints │Endpoints │Endpoints │Endpoints │       │
│  └──────────┴──────────┴──────────┴──────────┴──────────┴──────┘
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
        ┌───────▼────┐ ┌─────▼───┐ ┌────▼──────┐
        │  Services  │ │ External│ │ Database  │
        │   Layer    │ │  APIs   │ │   Layer   │
        └────────────┘ └─────────┘ └───────────┘
```

## Core Components

### 1. Application Entry Point (`app.py`)

**Responsibilities:**
- Flask app initialization
- Blueprint registration
- CORS configuration
- Error handling
- Database initialization

**Key Routes:**
- Health check: `GET /health`
- API endpoints: `GET /api/*`

**Database Configuration:**
- Development: SQLite (instance/app.db)
- Production: PostgreSQL connection pool
- Auto-migrations on startup

### 2. Authentication Module (`authentication.py`)

**Responsibilities:**
- OAuth 2.0 with Etsy integration
- JWT token generation and validation
- User session management
- API key security

**Key Functions:**
- `get_auth_url()` - Generate Etsy OAuth login link
- `handle_oauth_callback()` - Process authorization code
- `validate_token()` - JWT validation decorator
- `refresh_token()` - Token refresh logic

**Flow:**
```
User Login Request
    ↓
Generate OAuth URL + Code Verifier
    ↓
User Authorizes on Etsy
    ↓
Callback with Auth Code
    ↓
Exchange for Access Token
    ↓
Create JWT Token
    ↓
Return to Frontend
```

### 3. Data Models (`models.py`)

**Core Entities:**

#### User
- Etsy user authentication
- Shop information
- JWT token management
- Timestamps (created_at, updated_at)

#### Order
- Etsy order data
- Production status tracking
- Item details with pricing
- Communication log
- Internal notes

#### OrderItem
- Individual items in orders
- Product details
- Quantity and pricing
- Customization notes

#### OrderNote
- Internal notes on orders
- Timestamps
- Note content

#### OrderCommunication
- Customer communication log
- Messages, emails, chat
- Inbound/outbound direction
- Timestamps

#### Filament
- Inventory tracking
- Material type and color
- Weight management
- Cost calculations
- Low stock alerts

#### Printer
- Bambu Lab printer registration
- Connection details (Cloud/LAN)
- Status tracking
- Job management

#### PrinterMaterial
- Materials loaded in AMS
- Slot tracking
- Weight and percentages
- Vendor information

#### ScheduledPrint
- Print job scheduling
- Queue management
- Priority levels
- Status tracking

#### PrinterNotification
- Notification preferences
- Alert configuration
- Webhook support

**Relationships:**
```
User
├── Orders (1:Many)
│   ├── OrderItems (1:Many)
│   ├── OrderNotes (1:Many)
│   └── OrderCommunications (1:Many)
├── Printers (1:Many)
│   ├── PrinterMaterials (1:Many)
│   ├── ScheduledPrints (1:Many)
│   └── PrinterNotifications (1:1)
└── Filaments (1:Many)
```

### 4. Etsy Integration (`etsy_api.py`)

**Responsibilities:**
- Etsy OAuth integration
- Order synchronization
- Shop data retrieval
- Rate limiting compliance

**Key Functions:**
- `sync_orders()` - Fetch new orders from Etsy
- `get_shop_info()` - Retrieve shop details
- `update_listing_quantity()` - Sync inventory
- `send_tracking_number()` - Fulfill orders

**Rate Limiting:**
- Respects Etsy's 10 requests/minute limit
- Implements backoff strategy
- Queues bulk operations

### 5. Bambu Lab Integration

**Printer Types Supported:**
- Bambu Lab P1 Series
- Bambu Lab X1 Series
- Bambu Lab X1 Carbon

**Connection Methods:**

#### Cloud Connection (Recommended)
- Uses Bambu Connect cloud
- More reliable
- Works across networks
- Requires internet
- API endpoint: `https://api.bambulab.com/v1`

#### LAN Connection
- Direct local network
- Lower latency
- Faster response times
- Requires local network access
- API endpoint: Printer IP address

**Capabilities:**
- Real-time status monitoring
- Print job management
- Material/AMS tracking
- Temperature monitoring
- Print notifications

### 6. Configuration Management (`config.py`)

**Environment-Aware:**
- Development: Debug mode, SQLite
- Testing: In-memory database
- Production: PostgreSQL, optimized

**Key Settings:**
```python
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///instance/app.db')
JWT_SECRET = os.getenv('JWT_SECRET')
ETSY_CLIENT_ID = os.getenv('ETSY_CLIENT_ID')
BAMBU_ACCESS_CODE = os.getenv('BAMBU_ACCESS_CODE')
```

## API Layer Structure

### Blueprint Organization

```
/api
├── /auth
│   ├── /login
│   ├── /callback
│   ├── /logout
│   └── /user
├── /orders
│   ├── GET / (list)
│   ├── GET /:id (detail)
│   ├── PUT /:id (update)
│   ├── POST /sync (sync from Etsy)
│   ├── /:id/notes (CRUD)
│   └── /:id/communications (CRUD)
├── /filaments
│   ├── GET / (list)
│   ├── POST / (create)
│   ├── PUT /:id (update)
│   └── DELETE /:id (delete)
├── /bambu/printers
│   ├── GET / (list)
│   ├── POST / (register)
│   ├── DELETE /:id (remove)
│   ├── GET /:id/status (real-time)
│   ├── /materials (AMS management)
│   └── /scheduled-prints (queue)
└── /analytics
    ├── /dashboard (overview)
    └── /revenue (reports)
```

## Database Schema

### User Table
```sql
CREATE TABLE "user" (
  id INTEGER PRIMARY KEY,
  etsy_user_id VARCHAR,
  username VARCHAR UNIQUE,
  first_name VARCHAR,
  shop_id VARCHAR,
  shop_name VARCHAR,
  jwt_token TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Order Table
```sql
CREATE TABLE "order" (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  etsy_order_id VARCHAR,
  buyer_name VARCHAR,
  buyer_email VARCHAR,
  status VARCHAR,
  production_status VARCHAR,
  total_amount NUMERIC,
  currency VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES "user"(id)
);
```

### Printer Table
```sql
CREATE TABLE printer (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  name VARCHAR,
  type VARCHAR,
  serial_number VARCHAR,
  connection_type VARCHAR,
  status VARCHAR,
  created_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES "user"(id)
);
```

## Request/Response Flow

### Authentication Flow

```
1. Frontend requests login URL
   GET /api/auth/login
   
2. Backend returns Etsy OAuth URL
   {
     "auth_url": "https://www.etsy.com/oauth/...",
     "code_verifier": "..."
   }
   
3. User logs in on Etsy
   
4. Etsy redirects to frontend callback
   Frontend has: authorization_code, code_verifier
   
5. Frontend sends to backend
   POST /api/auth/callback
   {
     "code": "auth_code",
     "code_verifier": "verifier"
   }
   
6. Backend exchanges for access token
   Etsy API ← → Backend
   
7. Backend creates JWT
   Returns JWT to frontend
   
8. All future requests use JWT
   Authorization: Bearer {jwt_token}
```

### Order Sync Flow

```
Frontend triggers sync
   ↓
Backend queries Etsy API
   ↓
Fetches new orders since last sync
   ↓
Transforms Etsy format to internal models
   ↓
Stores in PostgreSQL
   ↓
Returns summary to frontend
   ↓
Frontend updates UI
```

## Error Handling

**Global Error Handler:**
- Catches all exceptions
- Logs to console and file
- Returns consistent JSON error response
- Includes status code and message

**Error Response Format:**
```json
{
  "error": "Description of error",
  "status": 400,
  "details": "Additional context if available"
}
```

**Common Scenarios:**
- Invalid JWT → 401 Unauthorized
- Missing resource → 404 Not Found
- Database error → 500 Internal Server Error
- Rate limit → 429 Too Many Requests

## Security

### Authentication
- JWT-based with PyJWT
- Token expiration (24 hours default)
- Secure secret key management

### Authorization
- User isolation (users see only their data)
- Role-based access (admin/user)
- API key validation

### Data Protection
- HTTPS in production
- Parameterized queries (SQLAlchemy prevents SQL injection)
- CORS configuration
- Input validation on all endpoints

### Secrets Management
- Environment variables for sensitive data
- No hardcoded credentials
- .env file (not in version control)

## Performance Optimization

### Database
- Connection pooling (SQLAlchemy)
- Indexed queries on frequently used columns
- Lazy loading for relationships
- Batch operations where possible

### Caching
- Query results cached in memory
- Etsy API response caching (5 minutes)
- Printer status caching (1 minute)

### Rate Limiting
- Per-user request limits
- Etsy API compliance (10 req/min)
- Gradual backoff on failures

## Monitoring & Logging

### Log Levels
- **DEBUG**: Detailed request/response data
- **INFO**: Application events
- **WARNING**: Potential issues
- **ERROR**: Failed operations

### Metrics Tracked
- Request count and timing
- Database query performance
- API integration latency
- Error rates by endpoint

## Deployment

### Docker
- Flask development server
- Gunicorn in production
- PostgreSQL container
- Environment configuration via docker-compose

### Environment Stages

**Development:**
- Debug mode enabled
- Verbose logging
- Hot reload
- SQLite database

**Staging:**
- Debug mode disabled
- PostgreSQL database
- Full logging
- Etsy sandbox API

**Production:**
- Performance optimized
- Minimal logging
- PostgreSQL with backups
- Etsy production API

## Future Enhancements

- [ ] Multiple printer types (Prusa, Creality)
- [ ] Advanced scheduling and queuing
- [ ] Machine learning for time estimation
- [ ] Webhook integrations
- [ ] Multi-user shop support
- [ ] Automated billing and invoicing
