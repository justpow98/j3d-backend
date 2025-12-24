# Bambu Connect Integration Guide

## Overview
This document covers the Bambu Connect features added to the J3D backend system. These features enable remote monitoring, material management, push notifications, and print scheduling for Bambu Lab 3D printers.

## New Database Models

### 1. BambuMaterial
Tracks materials/filaments loaded on Bambu printer AMS (Automated Material System)

**Fields:**
- `id`: Primary key
- `user_id`: Foreign key to User
- `printer_id`: Foreign key to Printer
- `slot`: AMS slot number (0-7)
- `material_type`: Material type (PLA, ABS, PETG, TPU, etc.)
- `color`: Material color
- `weight_grams`: Initial weight of material
- `remaining_pct`: Percentage of material remaining (0-100)
- `vendor`: Material vendor/brand
- `cost_per_kg`: Cost per kilogram for cost tracking
- `loaded_at`: When material was loaded
- `last_synced`: When synced with Bambu Connect
- `created_at`, `updated_at`: Timestamps

**Methods:**
- `to_dict()`: Serializes to JSON including calculated `remaining_grams`

### 2. PrintNotification
Manages push notification preferences for printers

**Fields:**
- `id`: Primary key
- `user_id`: Foreign key to User
- `printer_id`: Foreign key to Printer
- `notify_print_start`: Boolean - alert when print starts
- `notify_print_complete`: Boolean - alert when print finishes
- `notify_print_failed`: Boolean - alert on print failure
- `notify_material_change`: Boolean - alert when material needs changing
- `notify_maintenance`: Boolean - alert for maintenance events
- `email_enabled`: Boolean - send email notifications
- `webhook_url`: Optional custom webhook URL for integrations
- `created_at`, `updated_at`: Timestamps

**Methods:**
- `to_dict()`: JSON serialization

### 3. ScheduledPrint
Manages print job scheduling and queuing for Bambu printers

**Fields:**
- `id`: Primary key
- `user_id`: Foreign key to User
- `printer_id`: Foreign key to Printer
- `order_id`: Optional link to Etsy Order
- `job_name`: Human-readable print job name
- `file_name`: 3D model file name (STL/OBJ)
- `status`: Job status (queued, scheduled, started, completed, failed, cancelled)
- `scheduled_start`: When to start the print
- `estimated_duration_minutes`: Estimated print time
- `material_type`: Material to use (PLA, ABS, etc.)
- `material_slot`: AMS slot to use
- `nozzle_temp`: Nozzle temperature (°C)
- `bed_temp`: Bed temperature (°C)
- `print_speed`: Print speed (mm/s)
- `started_at`: Actual start timestamp
- `completed_at`: Actual completion timestamp
- `failed_reason`: Reason if print failed
- `priority`: Print queue priority (higher = sooner)
- `notes`: Additional notes/comments
- `created_at`, `updated_at`: Timestamps

**Methods:**
- `to_dict()`: JSON serialization

## API Endpoints

### Material Management

#### GET `/api/bambu/materials/<printer_id>`
Get all materials loaded on a printer

**Response:**
```json
[
  {
    "id": 1,
    "printer_id": 1,
    "slot": 0,
    "material_type": "PLA",
    "color": "White",
    "weight_grams": 250,
    "remaining_pct": 85,
    "remaining_grams": 212.5,
    "vendor": "Bambu Lab",
    "cost_per_kg": 25.00,
    "loaded_at": "2025-12-20T10:00:00",
    "last_synced": "2025-12-24T15:30:00"
  }
]
```

#### POST `/api/bambu/materials/<printer_id>`
Add a material to printer slot

**Request:**
```json
{
  "slot": 0,
  "material_type": "PLA",
  "color": "White",
  "weight_grams": 250,
  "remaining_pct": 100,
  "vendor": "Bambu Lab",
  "cost_per_kg": 25.00
}
```

**Response:** 201 Created (returns full material object)

#### PUT `/api/bambu/materials/<material_id>`
Update material status (remaining percentage, etc.)

**Request:**
```json
{
  "remaining_pct": 72,
  "material_type": "PLA",
  "color": "White",
  "weight_grams": 250
}
```

**Response:** 200 OK (returns updated material object)

### Notification Management

#### GET `/api/bambu/notifications/<printer_id>`
Get notification preferences for a printer

**Response:**
```json
{
  "id": 1,
  "printer_id": 1,
  "notify_print_start": true,
  "notify_print_complete": true,
  "notify_print_failed": true,
  "notify_material_change": false,
  "notify_maintenance": true,
  "email_enabled": true,
  "webhook_url": null
}
```

#### PUT `/api/bambu/notifications/<printer_id>`
Update notification preferences

**Request:**
```json
{
  "notify_print_start": true,
  "notify_print_complete": true,
  "notify_print_failed": true,
  "notify_material_change": true,
  "notify_maintenance": true,
  "email_enabled": true,
  "webhook_url": "https://webhook.site/your-endpoint"
}
```

**Response:** 200 OK (returns updated notification settings)

### Print Scheduling

#### GET `/api/bambu/scheduled-prints/<printer_id>`
Get all scheduled prints for a printer

**Query Parameters:**
- `status`: Optional filter by status (queued, scheduled, started, completed, failed, cancelled)

**Response:**
```json
[
  {
    "id": 1,
    "printer_id": 1,
    "order_id": 5,
    "job_name": "Order #12345 - Custom Bracket",
    "file_name": "custom_bracket.stl",
    "status": "queued",
    "scheduled_start": null,
    "estimated_duration_minutes": 120,
    "material_type": "PLA",
    "material_slot": 0,
    "nozzle_temp": 200,
    "bed_temp": 60,
    "print_speed": 50,
    "priority": 10,
    "notes": "Quantity: 2",
    "created_at": "2025-12-24T15:00:00"
  }
]
```

#### POST `/api/bambu/scheduled-prints`
Create a new scheduled print job

**Request:**
```json
{
  "printer_id": 1,
  "order_id": 5,
  "job_name": "Desk Organizer",
  "file_name": "desk_organizer.stl",
  "status": "queued",
  "scheduled_start": "2025-12-25T08:00:00",
  "estimated_duration_minutes": 180,
  "material_type": "PLA",
  "material_slot": 0,
  "nozzle_temp": 200,
  "bed_temp": 60,
  "print_speed": 50,
  "priority": 5,
  "notes": "Customer requested white filament"
}
```

**Response:** 201 Created

#### PUT `/api/bambu/scheduled-prints/<print_id>`
Update a scheduled print job

**Request:**
```json
{
  "status": "started",
  "priority": 1,
  "notes": "Print started successfully"
}
```

**Special Status Updates:**
- `status: "started"` - Automatically sets `started_at` to current time
- `status: "completed"` - Automatically sets `completed_at` to current time
- `status: "failed"` with `failed_reason` - Sets `completed_at` and failure reason

**Response:** 200 OK

#### DELETE `/api/bambu/scheduled-prints/<print_id>`
Cancel/delete a scheduled print job

**Response:** 200 OK with message

#### GET `/api/bambu/scheduled-prints/<printer_id>/queue`
Get current print queue (queued and scheduled jobs only)

**Response:**
```json
[
  {
    "id": 1,
    "job_name": "Order #12345 - Bracket",
    "status": "queued",
    "priority": 10,
    "scheduled_start": "2025-12-25T08:00:00",
    "estimated_duration_minutes": 120
  },
  {
    "id": 2,
    "job_name": "Order #12346 - Stand",
    "status": "scheduled",
    "priority": 8,
    "scheduled_start": "2025-12-25T10:30:00",
    "estimated_duration_minutes": 240
  }
]
```

### Order Integration

#### POST `/api/orders/<order_id>/schedule-prints`
Automatically schedule all items in an order for printing

This endpoint creates `ScheduledPrint` records for each item in an order with intelligent scheduling:
- Reads product profiles to get print settings (temperature, speed, duration)
- Automatically chains jobs with time offsets
- Assigns higher priority to earlier items
- Links jobs to the order for tracking

**Request:**
```json
{
  "printer_id": 1,
  "material_type": "PLA",
  "start_offset_minutes": 0
}
```

**Response:** 201 Created
```json
{
  "message": "Scheduled 2 print jobs",
  "prints": [
    {
      "id": 10,
      "order_id": 5,
      "job_name": "Order #12345 - Custom Bracket",
      "status": "queued",
      "priority": 10,
      "estimated_duration_minutes": 120
    },
    {
      "id": 11,
      "order_id": 5,
      "job_name": "Order #12345 - Stand",
      "status": "queued",
      "priority": 9,
      "scheduled_start": "2025-12-25T02:15:00",
      "estimated_duration_minutes": 180
    }
  ]
}
```

## Backend Helper Functions

### `schedule_order_prints(user_id, order_id, printer_id, material_type=None, start_offset_minutes=0)`

Located in `etsy_api.py`, this function automates print scheduling for orders:

**Parameters:**
- `user_id`: User ID for authorization
- `order_id`: Order to schedule
- `printer_id`: Target printer
- `material_type`: Optional material override (defaults to product profile setting)
- `start_offset_minutes`: Minutes to delay first print (default 0)

**Returns:**
- List of created `ScheduledPrint` objects

**Behavior:**
1. Looks up Order and Printer (with user authorization check)
2. For each OrderItem:
   - Searches for matching ProductProfile
   - Creates ScheduledPrint with profile settings or defaults
   - Chains jobs with time offsets based on estimated duration
   - Assigns decreasing priority to later items
3. Commits all jobs atomically

**Example Usage:**
```python
from etsy_api import schedule_order_prints
from models import db

# Schedule all items in order #5 on printer #1
# Start immediately with PLA material
scheduled = schedule_order_prints(
    user_id=1,
    order_id=5,
    printer_id=1,
    material_type='PLA',
    start_offset_minutes=0
)

for print_job in scheduled:
    print(f"Created job: {print_job.job_name}")
```

## Integration Examples

### 1. Material Tracking Workflow
```javascript
// Get current materials on printer
GET /api/bambu/materials/1

// Update material as it runs low
PUT /api/bambu/materials/10
{
  "remaining_pct": 45,
  "notes": "Getting low, may need replacement"
}

// Add new material
POST /api/bambu/materials/1
{
  "slot": 1,
  "material_type": "PETG",
  "color": "Black",
  "weight_grams": 250,
  "vendor": "Bambu Lab",
  "cost_per_kg": 30.00
}
```

### 2. Order to Print Workflow
```javascript
// Sync orders from Etsy
POST /api/etsy/sync-orders
// Creates Order objects with items

// When order is ready to print, schedule it
POST /api/orders/5/schedule-prints
{
  "printer_id": 1,
  "material_type": "PLA"
}
// Creates ScheduledPrint for each item

// Monitor print queue
GET /api/bambu/scheduled-prints/1/queue

// Update job status as it progresses
PUT /api/bambu/scheduled-prints/10
{
  "status": "started"
}
```

### 3. Notification Setup
```javascript
// Configure notifications for a printer
PUT /api/bambu/notifications/1
{
  "notify_print_start": true,
  "notify_print_complete": true,
  "notify_print_failed": true,
  "email_enabled": true,
  "webhook_url": "https://your-server.com/webhooks/bambu"
}
```

## Database Migration

To apply these new models to your database:

**Option 1: Development (auto-migration)**
```bash
export FLASK_ENV=development
export AUTO_DB_CREATE=1
python app.py
```

**Option 2: Using Flask-Migrate (recommended for production)**
```bash
# Generate migration
flask --app app:create_app() db migrate -m "Add Bambu Connect features"

# Review migration in migrations/versions/
# Then apply:
flask --app app:create_app() db upgrade
```

**Option 3: Docker (automatic)**
```bash
docker-compose up
# Automatically runs migrations on startup
```

## Cost Tracking

Materials support cost tracking to calculate print economics:

- Each material has `cost_per_kg` and `weight_grams`
- `remaining_grams` is automatically calculated from `remaining_pct`
- Link materials to orders for per-item cost tracking
- Integrate with Product Profiles for margin calculations

## Future Enhancements

Potential additions to expand Bambu Connect integration:

1. **Print Notifications via Webhooks**
   - Send webhook events for print start/complete/fail
   - Trigger custom business logic (email notifications, Discord alerts, etc.)

2. **Advanced Scheduling**
   - Multi-printer job distribution
   - Automatic load balancing
   - Print time optimization

3. **Material Auto-Management**
   - Sync material levels from Bambu Cloud
   - Low-stock alerts
   - Automatic reorder suggestions

4. **Print Analytics**
   - Material usage per order
   - Printer utilization charts
   - Cost per print calculations
   - Quality metrics (failure rates, etc.)

5. **Bambu Cloud Sync**
   - Pull printer status directly from Bambu Cloud
   - Sync print history
   - Two-way control (send commands to printer)

## Notes

- All endpoints require authentication via JWT token
- User isolation is enforced (users can only access their own printers/jobs)
- Printer connection type determines what information is available
- Material slot numbers depend on your AMS configuration (0-7 for single AMS, 0-15 for dual AMS)
- Timestamps are UTC-based for consistency
