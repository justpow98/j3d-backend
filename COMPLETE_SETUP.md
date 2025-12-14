# J3D Complete Setup & Usage Guide

## Overview

J3D is a full-stack web application that:
- Integrates with Etsy using 3-legged OAuth
- Fetches your orders from the last 6 months (both completed and new)
- Tracks 3D printer filament inventory (PLA, ABS, PETG, etc.)
- Records filament usage per print/order with automatic inventory deduction

## Architecture

### Backend (Flask/Python)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (default) or PostgreSQL/MySQL
- **Authentication**: Etsy OAuth 3-legged + JWT tokens
- **API**: RESTful endpoints for orders and filament management

### Frontend (Angular)
- **Framework**: Angular 17 (standalone components)
- **Styling**: SCSS with responsive design
- **State Management**: RxJS observables
- **HTTP**: HttpClient with interceptor-ready architecture

## File Structure

### Backend Files Created
```
j3d-backend/
├── app.py                    # Main Flask application with all routes
├── config.py                 # Configuration management
├── models.py                 # SQLAlchemy database models
├── authentication.py         # OAuth and JWT token handling
├── etsy_api.py              # Etsy API integration
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (configured)
├── .env.example             # Template for .env
└── README.md                # Full documentation
```

### Frontend Files Created
```
j3d-frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── login/login.component.ts                 # OAuth login page
│   │   │   ├── oauth-callback/oauth-callback.component.ts  # OAuth handler
│   │   │   └── dashboard/dashboard.component.ts         # Main dashboard
│   │   ├── services/
│   │   │   ├── auth.service.ts                 # Authentication service
│   │   │   ├── order.service.ts                # Order management
│   │   │   └── filament.service.ts             # Filament operations
│   │   ├── models/types.ts                     # TypeScript interfaces
│   │   ├── guards/auth.guard.ts                # Route protection
│   │   └── app.routes.ts                       # Routing configuration
│   ├── app.component.ts                        # Root component
│   ├── index.html                              # HTML entry point
│   ├── main.ts                                 # Bootstrap
│   └── styles.scss                             # Global styles
├── angular.json                                # Angular CLI config
├── package.json                                # NPM dependencies
├── tsconfig.json                               # TypeScript config
├── tsconfig.app.json                           # App-specific TS config
└── SETUP.md                                    # Quick start
```

## Database Models

### User Model
Stores authenticated Etsy users with OAuth tokens.

### Order Model
Tracks Etsy orders with:
- Order ID, shop ID
- Customer info (name, email)
- Status (NEW, PAID, SHIPPED, etc.)
- Timestamps and filament usage tracking

### Filament Model
Inventory tracking for spools with:
- Material type (PLA, ABS, PETG, etc.)
- Color
- Initial and current weight
- Cost per gram (optional)

### FilamentUsage Model
Logs usage per print/order, automatically deducts from inventory.

## API Routes

### Authentication
```
GET  /api/auth/login                 - Get Etsy OAuth URL
POST /api/auth/callback              - Handle OAuth code exchange
GET  /api/auth/user                  - Get current user info (requires JWT)
POST /api/auth/logout                - Logout (requires JWT)
```

### Orders
```
POST /api/orders/sync                - Fetch orders from Etsy (requires JWT)
GET  /api/orders                     - Get all user orders (requires JWT)
GET  /api/orders/<order_id>          - Get specific order (requires JWT)
```

### Filament Inventory
```
GET  /api/filaments                  - Get all filaments (requires JWT)
POST /api/filaments                  - Create new filament (requires JWT)
PUT  /api/filaments/<filament_id>    - Update filament (requires JWT)
DELETE /api/filaments/<filament_id>  - Delete filament (requires JWT)
```

### Filament Usage
```
POST /api/filament-usage             - Record usage & deduct (requires JWT)
GET  /api/filament-usage/order/<id>  - Get usage for order (requires JWT)
```

## Installation Steps

### Prerequisites
- Python 3.9+ with pip
- Node.js 18+ with npm
- Etsy developer account

### Step 1: Get Etsy Credentials

1. Visit https://www.etsy.com/developers
2. Sign in with your Etsy account
3. Create a new app
4. Copy Client ID and Client Secret
5. Set redirect URI to: `http://localhost:4200/oauth-callback`

### Step 2: Setup Backend

```bash
cd j3d-backend

# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Edit .env file
# Add your ETSY_CLIENT_ID and ETSY_CLIENT_SECRET
# Change SECRET_KEY to a random string

# Run the server
python app.py
```

The backend will start on `http://localhost:5000`

### Step 3: Setup Frontend

```bash
cd j3d-frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will open at `http://localhost:4200`

## Using the Application

### 1. Login
- Click "Login with Etsy"
- Authorize the app on Etsy's website
- You'll be redirected back to the dashboard

### 2. Sync Orders
- Click "Sync from Etsy" button
- App fetches all orders from the last 6 months
- Shows both completed and new orders

### 3. Manage Filament
- Click "Filament Inventory" tab
- Click "Add Filament" to add a new spool
- Enter: Material, Color, Initial Amount (g), Current Amount (g)
- Optionally set cost per gram
- View usage progress with visual bar

### 4. Track Usage
- When you complete a print from an order
- Go to Orders tab
- Click "Add Filament Usage" on the order
- Select the filament used
- Enter amount used (grams)
- Amount automatically deducted from inventory

## Key Features

### Etsy OAuth Integration
- Secure 3-legged OAuth flow
- Automatic token refresh
- JWT session tokens for frontend

### Order Syncing
- Fetches 6 months of order history
- Pulls both completed and new/pending orders
- Includes customer details and items
- Tracks order status changes

### Filament Tracking
- Multiple spools with different materials/colors
- Visual progress bars
- Cost tracking per gram
- Usage history per order

### Dashboard
- Responsive, modern UI
- Tab-based navigation
- Modal forms for add/edit
- Real-time data updates

## Configuration

### Environment Variables (.env)

```
FLASK_ENV=development              # Flask environment
FLASK_DEBUG=True                  # Debug mode (disable in production)
DATABASE_URL=sqlite:///j3d.db     # Database URL (supports PostgreSQL, MySQL)

# Etsy API
ETSY_CLIENT_ID=your_id            # From Etsy developer portal
ETSY_CLIENT_SECRET=your_secret    # From Etsy developer portal
ETSY_REDIRECT_URI=http://localhost:4200/oauth-callback

# Security
SECRET_KEY=random-string          # For JWT signing
```

### CORS Configuration

Edit `config.py` if running on different URLs:
```python
CORS_ORIGINS = ['http://localhost:4200', 'http://localhost:3000']
```

## Database

### Default Setup
- SQLite database: `j3d.db`
- Auto-created on first run
- Stores locally in backend directory

### Change Database
Update `DATABASE_URL` in `.env`:
- PostgreSQL: `postgresql://user:password@localhost/j3d`
- MySQL: `mysql://user:password@localhost/j3d`

### Reset Database
Delete `j3d.db` and restart the server.

## Troubleshooting

### OAuth Not Working
1. Check `ETSY_REDIRECT_URI` matches Etsy app settings
2. Ensure frontend runs on `http://localhost:4200`
3. Check network tab for actual redirect URL

### CORS Errors
1. Verify backend CORS origins in `config.py`
2. Check frontend API URL in services (should be `http://localhost:5000/api`)

### Database Errors
1. Delete `j3d.db`
2. Restart backend
3. Check directory permissions

### Token Errors
1. Clear browser local storage
2. Logout and login again
3. Check JWT_EXPIRATION_HOURS in config

## Development Tips

### Backend
- Uses Flask development server with auto-reload
- Modify routes in `app.py`
- Modify models in `models.py`
- Logs appear in terminal

### Frontend
- Angular CLI auto-reloads on file changes
- Check browser console for errors
- Redux DevTools not needed (using RxJS directly)

## Security Notes

### Production Checklist
- [ ] Change `SECRET_KEY` to random 32+ char string
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use HTTPS (set `ETSY_REDIRECT_URI` to https://...)
- [ ] Use production database (PostgreSQL recommended)
- [ ] Set strong CORS origins
- [ ] Enable HTTPS in Angular build
- [ ] Use environment-specific configs

## Future Enhancements

- Multiple shop support
- CSV/PDF exports
- Filament cost analytics
- Email notifications
- Mobile app
- Advanced filtering
- Print time estimation

## Support & Issues

- Check README.md in each folder for specific details
- Review error messages in browser console and terminal
- Verify all environment variables are set
- Ensure both servers are running on correct ports

## License

MIT License - See LICENSE file in each directory
