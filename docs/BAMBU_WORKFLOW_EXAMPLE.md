# Bambu Connect Integration Workflow

## Complete End-to-End Example

This document walks through a realistic workflow using Bambu Connect features.

## Scenario
You receive an Etsy order for 2 custom parts from a customer. You want to:
1. Sync the order from Etsy
2. Load materials on your Bambu printer
3. Configure notifications
4. Schedule the prints automatically
5. Monitor progress

## Step-by-Step Implementation

### Step 1: Sync Order from Etsy

**Endpoint:** `POST /api/etsy/sync-orders`
```bash
curl -X POST http://localhost:5000/api/etsy/sync-orders \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "total_receipts": 5,
  "new_orders_saved": 1,
  "message": "Successfully synced 1 new orders"
}
```

This creates an Order with OrderItems:
- Order #12345 from customer john@example.com
  - Item 1: "Custom Desk Bracket" (qty: 1)
  - Item 2: "Cable Stand" (qty: 1)

### Step 2: View Your Printers

**Endpoint:** `GET /api/printers`
```bash
curl -X GET http://localhost:5000/api/printers \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Bambu Lab X1",
    "type": "bambu",
    "connection_type": "bambu_cloud",
    "status": "online",
    "current_job": null,
    "utilization_pct": 0
  }
]
```

### Step 3: Check Current Materials

**Endpoint:** `GET /api/bambu/materials/1`
```bash
curl -X GET http://localhost:5000/api/bambu/materials/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
[
  {
    "id": 5,
    "printer_id": 1,
    "slot": 0,
    "material_type": "PLA",
    "color": "White",
    "weight_grams": 250,
    "remaining_pct": 100,
    "remaining_grams": 250,
    "vendor": "Bambu Lab",
    "cost_per_kg": 25.00,
    "loaded_at": "2025-12-20T10:00:00",
    "last_synced": "2025-12-24T15:30:00"
  }
]
```

Material is ready! You have white PLA loaded.

### Step 4: Enable Notifications

**Endpoint:** `PUT /api/bambu/notifications/1`
```bash
curl -X PUT http://localhost:5000/api/bambu/notifications/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notify_print_start": true,
    "notify_print_complete": true,
    "notify_print_failed": true,
    "notify_material_change": false,
    "notify_maintenance": true,
    "email_enabled": true,
    "webhook_url": "https://webhook.site/your-unique-endpoint"
  }'
```

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
  "webhook_url": "https://webhook.site/your-unique-endpoint",
  "updated_at": "2025-12-24T16:00:00"
}
```

You'll now get notifications when prints start, complete, or fail.

### Step 5: Schedule Order for Printing

**Endpoint:** `POST /api/orders/1/schedule-prints`
```bash
curl -X POST http://localhost:5000/api/orders/1/schedule-prints \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "printer_id": 1,
    "material_type": "PLA",
    "start_offset_minutes": 0
  }'
```

**Behind the Scenes:**
1. Reads Order #12345 (2 items)
2. Looks up ProductProfile for "Custom Desk Bracket"
   - Estimated print time: 120 minutes
   - Nozzle temp: 200°C, Bed: 60°C
   - Speed: 50 mm/s
3. Creates ScheduledPrint #1 for "Custom Desk Bracket"
   - Status: queued
   - Priority: 10 (higher priority)
   - Scheduled start: immediately
4. Chains next print 120 min + 15 min buffer later
5. Creates ScheduledPrint #2 for "Cable Stand"
   - Status: queued
   - Priority: 9 (slightly lower)
   - Scheduled start: 2:15 hours from now
   - Est. duration: 180 min (different product profile)

**Response:**
```json
{
  "message": "Scheduled 2 print jobs",
  "prints": [
    {
      "id": 10,
      "printer_id": 1,
      "order_id": 1,
      "job_name": "Order #12345 - Custom Desk Bracket",
      "file_name": "custom_desk_bracket.stl",
      "status": "queued",
      "scheduled_start": null,
      "estimated_duration_minutes": 120,
      "material_type": "PLA",
      "material_slot": 0,
      "nozzle_temp": 200,
      "bed_temp": 60,
      "print_speed": 50,
      "priority": 10,
      "notes": "Quantity: 1"
    },
    {
      "id": 11,
      "printer_id": 1,
      "order_id": 1,
      "job_name": "Order #12345 - Cable Stand",
      "file_name": "cable_stand.stl",
      "status": "queued",
      "scheduled_start": "2025-12-24T18:15:00",
      "estimated_duration_minutes": 180,
      "material_type": "PLA",
      "material_slot": 0,
      "nozzle_temp": 200,
      "bed_temp": 60,
      "print_speed": 50,
      "priority": 9,
      "notes": "Quantity: 1"
    }
  ]
}
```

### Step 6: Check Print Queue

**Endpoint:** `GET /api/bambu/scheduled-prints/1/queue`
```bash
curl -X GET http://localhost:5000/api/bambu/scheduled-prints/1/queue \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
[
  {
    "id": 10,
    "job_name": "Order #12345 - Custom Desk Bracket",
    "status": "queued",
    "priority": 10,
    "scheduled_start": null,
    "estimated_duration_minutes": 120
  },
  {
    "id": 11,
    "job_name": "Order #12345 - Cable Stand",
    "status": "queued",
    "priority": 9,
    "scheduled_start": "2025-12-24T18:15:00",
    "estimated_duration_minutes": 180
  }
]
```

Queue is ready! First job will start immediately, second queued for later.

### Step 7: Printer Starts First Job

You manually start the first job on your Bambu printer (or it auto-starts).

**Endpoint:** `PUT /api/bambu/scheduled-prints/10`
```bash
curl -X PUT http://localhost:5000/api/bambu/scheduled-prints/10 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "started"
  }'
```

**Response:**
```json
{
  "id": 10,
  "status": "started",
  "started_at": "2025-12-24T16:05:00",
  "job_name": "Order #12345 - Custom Desk Bracket"
}
```

**Backend Action:**
- Sets `started_at` to current timestamp
- Sends notification webhook (if configured)
- Sends email alert (if email notifications enabled)

### Step 8: Monitor Print Progress

While print is running, you can check status:

**Endpoint:** `GET /api/printer-connections/1/status`
```bash
curl -X GET http://localhost:5000/api/printer-connections/1/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response (from Bambu Lab printer):**
```json
{
  "printer_name": "Bambu Lab X1",
  "connection_type": "bambu_cloud",
  "state": "printing",
  "progress_percent": 45,
  "layers_printed": 180,
  "total_layers": 400,
  "nozzle_temp": 200,
  "bed_temp": 62,
  "chamber_temp": 35,
  "errors": null,
  "last_updated": "2025-12-24T16:35:00"
}
```

Print is 45% done!

### Step 9: First Job Completes

Two hours later (120 min + 15 min buffer), first print finishes.

**Endpoint:** `PUT /api/bambu/scheduled-prints/10`
```bash
curl -X PUT http://localhost:5000/api/bambu/scheduled-prints/10 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

**Response:**
```json
{
  "id": 10,
  "status": "completed",
  "started_at": "2025-12-24T16:05:00",
  "completed_at": "2025-12-24T18:05:00",
  "estimated_duration_minutes": 120,
  "job_name": "Order #12345 - Custom Desk Bracket"
}
```

**Backend Action:**
- Sets `completed_at` to current timestamp
- Sends "Print Complete" notification
- Second print automatically becomes next in queue

### Step 10: Check Material Usage

Update material remaining percentage based on actual usage:

**Endpoint:** `PUT /api/bambu/materials/5`
```bash
curl -X PUT http://localhost:5000/api/bambu/materials/5 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "remaining_pct": 82
  }'
```

**Response:**
```json
{
  "id": 5,
  "slot": 0,
  "material_type": "PLA",
  "weight_grams": 250,
  "remaining_pct": 82,
  "remaining_grams": 205,
  "vendor": "Bambu Lab",
  "cost_per_kg": 25.00,
  "last_synced": "2025-12-24T18:10:00"
}
```

Tracking shows ~45g of white PLA was used for the bracket.

### Step 11: Second Job Completes

**Endpoint:** `PUT /api/bambu/scheduled-prints/11`
```bash
curl -X PUT http://localhost:5000/api/bambu/scheduled-prints/11 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

Both prints for Order #12345 are now complete!

**Endpoint:** `GET /api/orders/1`
```bash
curl -X GET http://localhost:5000/api/orders/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

You can see the order is complete with:
- All items printed
- Total print time: 300 minutes
- Material used: ~75g white PLA
- Cost: ~$1.88 in materials
- Status ready for packing and shipment

---

## Integration with Your Frontend

### Material Management UI
- Show current materials on each printer
- Allow updating remaining percentage with visual gauge
- One-click "Add Material" form for new spools

### Print Scheduling UI
- Drag-and-drop job queue reordering
- Calendar view of scheduled prints
- Real-time progress bar
- Email/webhook notification settings

### Order Dashboard
- "Schedule for Printing" button on each order
- View related print jobs
- Track material cost per order
- Print history with photos

### Notifications
- Desktop notifications when prints complete
- Email alerts for failures
- Webhook integration for custom alerts (Discord, Slack, etc.)

---

## Cost Tracking Example

From the workflow above:

**Materials Used:**
- Item 1: ~45g PLA @ $25/kg = ~$1.13
- Item 2: ~30g PLA @ $25/kg = ~$0.75
- Total material cost: ~$1.88

**With Product Profiles:**
Each product has:
- Material cost: $1.13 + $0.75
- Labor (2 items × 30 min): $15 (@ $15/hr)
- Overhead: $0.50
- Total cost: ~$17.26
- Target margin: 40%
- Suggested price: $24.16

**Actual Order Price:** $30 (from Etsy)
**Profit:** $12.74 (42% margin) ✓

---

## Error Handling Example

If second print fails:

**Endpoint:** `PUT /api/bambu/scheduled-prints/11`
```bash
curl -X PUT http://localhost:5000/api/bambu/scheduled-prints/11 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "failed",
    "failed_reason": "Filament ran out mid-print, nozzle clogged"
  }'
```

**Response:**
```json
{
  "id": 11,
  "status": "failed",
  "failed_reason": "Filament ran out mid-print, nozzle clogged",
  "completed_at": "2025-12-24T20:30:00"
}
```

**Backend Action:**
- Sends "Print Failed" notification
- Marks job as failed with reason
- Allows manual retry/rescheduling
- Logs failure for analytics

You can then:
1. Fix the issue (reload filament, clear nozzle)
2. Reschedule job by updating status back to "queued"
3. Or delete and create new scheduled print

---

## Summary

This workflow demonstrates:
✅ Order syncing from Etsy
✅ Material management tracking
✅ Automated print scheduling with intelligent chaining
✅ Push notifications for events
✅ Progress monitoring
✅ Status updates and completion tracking
✅ Cost tracking and analytics
✅ Error handling and recovery

All with a simple, intuitive API that integrates seamlessly with your Bambu Lab X1!
