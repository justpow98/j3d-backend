# Backend Documentation Index

## Quick Navigation

### For Different Use Cases:

**📚 I need API reference**
→ [API.md](API.md) - Complete endpoint documentation with examples

**🏗️ I need to understand the architecture**
→ [ARCHITECTURE.md](ARCHITECTURE.md) - System design and component overview

**🖨️ I need to set up a 3D printer**
→ [PRINTER_SETUP.md](PRINTER_SETUP.md) - Complete printer setup guide for Bambu Lab

**💾 I need database help**
→ [DATABASE.md](DATABASE.md) - Database setup, migrations, and management

**🎯 I want Bambu Connect features**
→ [BAMBU_CONNECT_FEATURES.md](BAMBU_CONNECT_FEATURES.md) - Complete Bambu Connect API reference

**📋 I want Bambu Connect overview**
→ [BAMBU_CONNECT_SUMMARY.md](BAMBU_CONNECT_SUMMARY.md) - Quick summary of Bambu Connect

**🔄 I want a real workflow example**
→ [BAMBU_WORKFLOW_EXAMPLE.md](BAMBU_WORKFLOW_EXAMPLE.md) - Step-by-step workflow with curl examples

**🔧 I want implementation details**
→ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - What code changed and why

**🎨 I need system diagrams**
→ [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) - Visual system design and data flows

---

## Documentation Files

### Core Documentation (Required Reading)

| File | Size | Purpose | Audience |
|------|------|---------|----------|
| [API.md](API.md) | 1200+ lines | Complete API reference | Developers, API consumers |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 500+ lines | System architecture & design | Architects, senior devs |
| [DATABASE.md](DATABASE.md) | 800+ lines | Database setup & management | DevOps, backend devs |
| [PRINTER_SETUP.md](PRINTER_SETUP.md) | 600+ lines | Printer integration guide | End users, integrators |

### Bambu Connect Documentation (Feature-Specific)

| File | Size | Purpose | Audience |
|------|------|---------|----------|
| [BAMBU_CONNECT_FEATURES.md](BAMBU_CONNECT_FEATURES.md) | 560+ lines | Complete API reference | Frontend devs, API users |
| [BAMBU_CONNECT_SUMMARY.md](BAMBU_CONNECT_SUMMARY.md) | 150+ lines | Feature overview | Managers, quick reference |
| [BAMBU_WORKFLOW_EXAMPLE.md](BAMBU_WORKFLOW_EXAMPLE.md) | 500+ lines | Real-world examples | Frontend devs, integrators |
| [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) | 400+ lines | System design diagrams | Architects, designers |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | 300+ lines | Code changes detail | Reviewers, deployers |

---

## Feature Summary

### Core Features
✅ Order management from Etsy  
✅ Filament/material inventory tracking  
✅ 3D printer integration (Bambu Lab)  
✅ Print scheduling and queuing  
✅ Material tracking with usage  
✅ Notification system (email, webhooks)  
✅ Authentication with Etsy OAuth  
✅ User isolation and security  

### API Endpoints: 25+
- Authentication: 4 endpoints
- Order management: 6 endpoints
- Filament management: 4 endpoints
- Printer management: 4 endpoints
- Bambu Connect: 11 endpoints
- Analytics: 2 endpoints

---

## Getting Started Paths

### Path 1: API Developer (Frontend Integration)
1. Read [BAMBU_CONNECT_SUMMARY.md](BAMBU_CONNECT_SUMMARY.md) (5 min)
2. Study [BAMBU_CONNECT_FEATURES.md](BAMBU_CONNECT_FEATURES.md) (30 min)
3. Follow [BAMBU_WORKFLOW_EXAMPLE.md](BAMBU_WORKFLOW_EXAMPLE.md) (20 min)
4. Reference [API.md](API.md) as needed

### Path 2: System Architect
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) (30 min)
2. Study [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) (20 min)
3. Review [DATABASE.md](DATABASE.md) (20 min)
4. Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for details

### Path 3: DevOps/Deployment
1. Read [DATABASE.md](DATABASE.md) - Setup section (15 min)
2. Follow [PRINTER_SETUP.md](PRINTER_SETUP.md) if using Bambu Lab (20 min)
3. Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Deployment section (10 min)

### Path 4: End User/Shop Setup
1. Start with [PRINTER_SETUP.md](PRINTER_SETUP.md) (30 min)
2. Reference [BAMBU_WORKFLOW_EXAMPLE.md](BAMBU_WORKFLOW_EXAMPLE.md) for operations (20 min)
3. Check [BAMBU_CONNECT_SUMMARY.md](BAMBU_CONNECT_SUMMARY.md) for features (10 min)

---

## Technology Stack

**Backend:**
- Flask 3.0.0 - Web framework
- SQLAlchemy 3.1 - ORM
- PostgreSQL 15 - Database (production)
- SQLite - Database (development)
- JWT - Authentication

**Integrations:**
- Etsy API v3 - Order management
- Bambu Lab APIs - Printer control

**Deployment:**
- Docker & Docker Compose
- Gunicorn - WSGI server
- Nginx - Reverse proxy

---

## Quick Reference

### Database Tables
```
user (users with Etsy OAuth)
├── orders (Etsy orders)
│   ├── order_items
│   ├── order_notes
│   ├── order_communications
│   └── scheduled_prints (Bambu)
├── filaments (inventory)
├── printers (3D printers)
│   ├── bambu_materials (loaded materials)
│   ├── printer_notifications (alert settings)
│   └── scheduled_prints (print jobs)
└── analytics (usage tracking)
```

### API Routes
```
/api/auth/*              - Authentication
/api/orders/*            - Order management
/api/filaments/*         - Inventory
/api/printers/*          - Printer info
/api/bambu/*             - Bambu Connect features
/api/analytics/*         - Reports
```

### Key Concepts
- **User Isolation**: Each user sees only their own data
- **OAuth Integration**: Uses Etsy's 3-legged OAuth for auth
- **JWT Tokens**: Secures API endpoints
- **Print Scheduling**: Intelligent job queuing with time offsets
- **Material Tracking**: Tracks usage per print job
- **Notifications**: Email and webhook support

---

## Common Tasks

### I want to...

**Add a new API endpoint**
1. Define model in `models.py` if needed
2. Add route in `app.py`
3. Document in [API.md](API.md)
4. Test with curl examples from [BAMBU_WORKFLOW_EXAMPLE.md](BAMBU_WORKFLOW_EXAMPLE.md)

**Set up a database migration**
→ See [DATABASE.md](DATABASE.md) - Migrations section

**Integrate Bambu Lab printer**
→ See [PRINTER_SETUP.md](PRINTER_SETUP.md)

**Understand the print scheduling**
→ See [BAMBU_WORKFLOW_EXAMPLE.md](BAMBU_WORKFLOW_EXAMPLE.md) - Steps 5-6

**Deploy to production**
→ See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Deployment section

**Query the database**
→ See [DATABASE.md](DATABASE.md) - Monitoring section

---

## File Organization

```
j3d-backend/
├── app.py                          (Main application - 2200+ lines)
├── models.py                       (Data models - 800+ lines)
├── authentication.py               (OAuth & JWT)
├── etsy_api.py                     (Etsy integration)
├── config.py                       (Configuration)
├── requirements.txt                (Dependencies)
├── README.md                       (Quick overview)
└── docs/
    ├── INDEX.md                   ← You are here
    ├── API.md                     (Complete API reference)
    ├── ARCHITECTURE.md            (System design)
    ├── DATABASE.md                (Database guide)
    ├── PRINTER_SETUP.md           (Printer integration)
    ├── BAMBU_CONNECT_FEATURES.md  (Bambu API reference)
    ├── BAMBU_CONNECT_SUMMARY.md   (Bambu overview)
    ├── BAMBU_WORKFLOW_EXAMPLE.md  (Bambu examples)
    ├── ARCHITECTURE_DIAGRAM.md    (System diagrams)
    └── IMPLEMENTATION_SUMMARY.md  (Code changes)
```

---

## Documentation Statistics

- **Total Pages**: 8 core docs + 5 Bambu-specific docs
- **Total Lines**: 5000+ lines of comprehensive documentation
- **API Endpoints**: 25+ documented with examples
- **Code Examples**: 50+ curl examples and code snippets
- **Diagrams**: 10+ ASCII diagrams showing flows and relationships

---

## Support & Contact

For documentation issues or questions:
1. Check the relevant doc file for your use case
2. Follow the examples in [BAMBU_WORKFLOW_EXAMPLE.md](BAMBU_WORKFLOW_EXAMPLE.md)
3. Review the architecture in [ARCHITECTURE.md](ARCHITECTURE.md)
4. Check code comments in the source files

---

## Last Updated

December 24, 2025

## Version

Backend: 3.0  
Frontend: 2.0  
Documentation: 2.0
