# Bambu Connect Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Angular)                       │
│  (To be built: Material UI, Print Queue, Notifications)     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask Backend (app.py)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐  │
│  │  Bambu Material │  │  Notification    │  │  Scheduled │  │
│  │   Endpoints     │  │   Endpoints      │  │   Prints   │  │
│  │                 │  │                  │  │  Endpoints │  │
│  │  GET/POST/PUT   │  │  GET/PUT         │  │            │  │
│  │  /api/bambu/    │  │  /api/bambu/     │  │  GET/POST/ │  │
│  │   materials/*   │  │  notifications/* │  │   PUT/DEL  │  │
│  └────────┬────────┘  └────────┬─────────┘  │  /api/     │  │
│           │                    │           │bambu/      │  │
│           │                    │           │scheduled-  │  │
│           └────────────────────┼──────────▶│ prints/*   │  │
│                                │           │            │  │
│                  Order Integration         │ + /api/    │  │
│                  POST /api/orders/         │ orders/<id>│  │
│                  <id>/schedule-prints      │ /schedule  │  │
│                                            │ -prints    │  │
│                                            └────┬───────┘  │
└──────────────────────────────────────────────────┼──────────┘
                                                   │
                                  ┌────────────────┼─────────────┐
                                  ▼                ▼              ▼
┌─────────────────────────┐  ┌──────────────┐  ┌────────────────┐
│   SQLAlchemy Models     │  │  EtsyAPI     │  │ Helper Function│
│   (models.py)           │  │  (etsy_api.  │  │  schedule_     │
│                         │  │   py)        │  │  order_prints()│
│  - BambuMaterial        │  │              │  │                │
│  - PrintNotification    │  │ Orders from  │  │ Auto-schedule  │
│  - ScheduledPrint       │  │ Etsy API     │  │ order items    │
│  (+ existing models)    │  │              │  │                │
└────────────┬────────────┘  └──────┬───────┘  └────────────────┘
             │                      │
             │      Database        │
             ▼      Connection      ▼
    ┌────────────────────────────────────────┐
    │     SQLAlchemy ORM Layer               │
    │  (db.session, relationships, etc.)     │
    └────────────────┬───────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
    ┌─────────────┐           ┌──────────────┐
    │  SQLite     │           │  PostgreSQL  │
    │  (dev/test) │           │  (production)│
    └─────────────┘           └──────────────┘
```

## Data Model Relationships

```
┌──────────────────────────────────────────────────────────────┐
│                         USER                                  │
│                                                                │
│  ├─ has many: orders                                          │
│  ├─ has many: printers                                        │
│  ├─ has many: bambu_materials (through printers)             │
│  ├─ has many: print_notifications (through printers)         │
│  └─ has many: scheduled_prints (through printers)            │
└──────────────────────────────────────────────────────────────┘
              │                    │
              ▼                    ▼
      ┌─────────────┐    ┌──────────────────┐
      │    ORDER    │    │    PRINTER       │
      │             │    │                  │
      │ - id        │    │ - id             │
      │ - user_id   │    │ - user_id        │
      │ - customer  │    │ - name           │
      │ - items     │    │ - connection     │
      └──────┬──────┘    └────────┬─────────┘
             │                    │
             │            ┌───────┴────────┐
             │            ▼                ▼
             │      ┌─────────────┐   ┌──────────────┐
             │      │ BAMBU       │   │ PRINT        │
             │      │ MATERIAL    │   │ NOTIFICATION │
             │      │             │   │              │
             │      │ - id        │   │ - id         │
             │      │ - printer   │   │ - printer    │
             │      │ - slot      │   │ - webhook    │
             │      │ - material  │   │ - email_en   │
             │      │ - remaining │   │ - flags      │
             │      └─────────────┘   └──────────────┘
             │
             ▼
      ┌──────────────────┐
      │ SCHEDULED PRINT  │
      │                  │
      │ - id             │
      │ - printer_id     │
      │ - order_id  ─────┼──────┐
      │ - job_name       │      │
      │ - status         │      │
      │ - material_slot  │      │
      │ - temps          │      │
      │ - priority       │      │
      └──────────────────┘      │
           │                    │
           └────────────────────┘
           (optional link to order)
```

## API Call Flow

```
1. User POSTs to /api/orders/<id>/schedule-prints
   │
   ├─ Validates order exists and user owns it
   ├─ Validates printer exists and user owns it
   │
   └─► schedule_order_prints() is called
       │
       ├─ Reads each OrderItem
       ├─ Looks up ProductProfile for print settings
       ├─ Creates ScheduledPrint #1
       │  ├─ Defaults: status=queued, scheduled_start=None
       │  └─ Settings: temps, speed, material from profile
       │
       ├─ Creates ScheduledPrint #2
       │  ├─ Chains: scheduled_start = now + duration1 + buffer
       │  └─ Settings: from ProductProfile or defaults
       │
       └─ Returns list of created prints
           │
           └─► Frontend shows queue with:
               ├─ Job names
               ├─ Priority ordering
               ├─ Scheduled start times
               └─ Estimated durations


2. Printer Monitoring (Real-time)
   │
   ├─ Frontend polls GET /api/printer-connections/<id>/status
   │  │
   │  └─► Bambu Cloud/LAN API returns current state
   │      ├─ progress_percent
   │      ├─ nozzle_temp, bed_temp, chamber_temp
   │      ├─ layers_printed / total_layers
   │      └─ errors (if any)
   │
   └─ Frontend updates:
      ├─ Progress bar
      ├─ Temperature gauges
      ├─ ETA countdown
      └─ Error alerts


3. Job Completion Update
   │
   ├─ User/System PUTs to /api/bambu/scheduled-prints/<id>
   │  └─ {"status": "completed"}
   │
   ├─ Backend:
   │  ├─ Sets completed_at = now
   │  ├─ Updates order status (if linked)
   │  └─ Triggers notifications
   │
   └─ Notifications:
      ├─ Email (if enabled)
      ├─ Webhook POST (if configured)
      └─ Frontend UI update
```

## Notification Flow

```
                    ┌─ Print Starts
                    │
        ScheduledPrint Status Changed
                    │
                    ├─ Print Completes  ───┐
                    │                       │
                    ├─ Print Fails      ───┼──→ Check PrintNotification settings
                    │                       │
                    └─ Material Ends    ───┤
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │ Notification  │
                                    │ Preferences?  │
                                    └───────────────┘
                                            │
                    ┌───────────────────────┼───────────────────┐
                    │                       │                   │
                    ▼                       ▼                   ▼
            notify_xxx = true       email_enabled = true  webhook_url?
                    │                       │                   │
                    ├──→ Send Email      ├──→ Email Alert   ├──→ POST webhook
                    │                   │                    │
                    └─────────────────────┴────────────────────┘
                                    │
                                    ▼
                            ┌──────────────────┐
                            │   User Gets      │
                            │   Notification   │
                            │                  │
                            │ - Email          │
                            │ - Webhook Alert  │
                            │ - UI Update      │
                            └──────────────────┘
```

## Workflow State Machine

```
                    ┌──────────┐
                    │ queued   │  (initial state, waiting in queue)
                    └──────┬───┘
                           │
                   (user clicks "start" or
                    printer auto-starts)
                           │
                           ▼
                    ┌──────────────┐
                    │ scheduled    │  (future scheduled time reached)
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ started      │  (actively printing)
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │ (print succeeds)        │ (print fails)
              │                         │
              ▼                         ▼
       ┌────────────┐           ┌──────────────┐
       │ completed  │           │ failed       │
       │ (done!)    │           │ (error)      │
       └────────────┘           └──────────────┘
              │                         │
              └─────────────┬───────────┘
                            │
                    ┌───────────────────┐
                    │ Can be deleted or │
                    │ rescheduled       │
                    └───────────────────┘
```

## Material Management Lifecycle

```
┌─────────────┐
│ New Spool   │  250g PLA @ $25/kg
│ (loaded)    │
└──────┬──────┘
       │ Remaining: 100%
       │
       ▼ During 1st print: used 45g
┌─────────────┐
│ In Use      │  205g remaining (82%)
│             │
└──────┬──────┘
       │ During 2nd print: used 30g
       │
       ▼
┌─────────────┐
│ Low Stock   │  175g remaining (70%)
│             │  ↓
└──────┬──────┘  Alert: "Getting low"
       │
       │ More prints...
       │
       ▼
┌─────────────┐
│ Critical    │  50g remaining (20%)
│ (< 30g)     │  ↓
└──────┬──────┘  Alert: "Replace spool"
       │
       │ One more quick print...
       │
       ▼
┌─────────────┐
│ Replace     │  5g remaining (2%)
│ Material    │  ↓
└──────┬──────┘  Stop - cannot print
       │
       │
       ▼
┌─────────────────────┐
│ Spool Depleted      │  0g (removed from AMS)
│ (historical record) │
└─────────────────────┘

Total Usage: 245g
Cost Used: ~$6.13 (245g ÷ 1000 × $25/kg)
```

## Integration Points

```
Etsy API
   │
   ├─► Order Syncing
   │   │
   │   ├─► Creates Order + OrderItems
   │   │
   │   └─► Triggers schedule_order_prints()
   │       │
   │       └─► Creates ScheduledPrint records
   │
   └─► Customer Information
       │
       └─► Links to Customer model


Bambu Lab API
   │
   ├─► Cloud API (Bambu Connect)
   │   ├─ Printer status
   │   ├─ Print progress
   │   └─ Material levels (if available)
   │
   └─► LAN API
       ├─ Local printer status
       ├─ Direct control
       └─ Real-time updates


ProductProfile
   │
   └─► Print Settings
       ├─ Nozzle/Bed temps
       ├─ Print speed
       ├─ Estimated duration
       └─ Material type/color


Frontend
   │
   └─► User Actions
       ├─ Schedule prints
       ├─ Configure notifications
       ├─ Track progress
       ├─ Update materials
       └─ View analytics
```

---

## Technology Stack

```
├─ Backend
│  ├─ Flask 3.0.0
│  ├─ SQLAlchemy 3.1.1
│  ├─ Flask-Migrate 4.0.7
│  └─ Flask-CORS 4.0.0
│
├─ Database
│  ├─ SQLite (development)
│  └─ PostgreSQL 15 (production)
│
├─ APIs
│  ├─ Etsy API v3
│  ├─ Bambu Lab Cloud API
│  ├─ Bambu Lab LAN API
│  └─ OpenWeatherMap
│
├─ Authentication
│  ├─ Etsy OAuth 3-legged
│  ├─ PKCE flow
│  └─ JWT tokens
│
└─ Deployment
   ├─ Docker containers
   ├─ docker-compose orchestration
   └─ Automated migrations
```

---

## Scalability Considerations

```
Current Architecture:
├─ Single Flask instance
├─ SQLite (dev) / PostgreSQL (prod)
├─ Synchronous REST API
└─ Polling for status updates

Scaling Up:
├─ Add load balancer
├─ Multiple Flask instances
├─ Redis for caching
├─ WebSocket for real-time updates
├─ Message queue (Celery) for async jobs
├─ Database read replicas
└─ Background workers for notifications
```

This completes the Bambu Connect feature implementation!
