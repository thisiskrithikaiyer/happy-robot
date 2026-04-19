# System Architecture & Data Flow

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  HappyRobot Platform                        │
│                                                             │
│   Web Call Trigger                                          │
│        │                                                    │
│        ▼                                                    │
│   AI Agent: Maya (Inbound Carrier Sales)                    │
│        │                                                    │
│        ├── Prompt (System Instructions)                     │
│        │                                                    │
│        ├── Tool: verify_carrier                             │
│        │       └── Webhook → GET /api/verify_carrier        │
│        │                                                    │
│        ├── Tool: search_load                                │
│        │       └── Webhook → GET /api/loads                 │
│        │                                                    │
│        └── Tool: log_offer                                  │
│                └── Webhook → POST /api/offers               │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS + X-API-Key
                         ▼
┌────────────────────────────────────────────────────────────┐
│           Flask API (Railway)                              │
│   happyrobot-carrier-sales-agent.up.railway.app            │
│                                                            │
│   GET  /api/verify_carrier  → FMCSA eligibility check      │
│   GET  /api/loads           → Search loads by preferences  │
│   POST /api/offers          → Log call outcome             │
│   GET  /api/metrics         → Aggregated analytics         │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│           SQLite Database                                  │
│                                                            │
│   Loads Table  — 15 sample loads                           │
│   Offers Table — call logs (outcome, price, sentiment)     │
└────────────────────────────────────────────────────────────┘
                         ▲
                         │ HTTPS (proxy)
┌────────────────────────┴───────────────────────────────────┐
│           Next.js Dashboard (Railway)                      │
│                                                            │
│   - Fetches /api/metrics every 5 seconds                   │
│   - Shows KPIs, sentiment, lanes, equipment breakdown      │
└────────────────────────────────────────────────────────────┘
```

## Call Lifecycle

```
1. Carrier triggers web call
        │
2. Maya greets → asks for MC number
        │
3. verify_carrier tool called
   GET /api/verify_carrier?mc=MC123456
   Response: { "eligible": true }
        │
4. Maya asks origin, destination, equipment type
        │
5. search_load tool called
   GET /api/loads?origin=Los+Angeles&destination=New+York&equipment_type=Dry+Van
   Response: [{ "load_id": "L001", "loadboard_rate": 2500, ... }]
        │
6. Maya pitches load → carrier negotiates (up to 3 rounds)
        │
7. log_offer tool called
   POST /api/offers
   Body: {
     "carrier_mc": "MC123456",
     "negotiated_price": 2375,
     "outcome": "agreed",
     "sentiment": "positive",
     "origin": "Los Angeles, CA",
     "destination": "New York, NY",
     "equipment_type": "Dry Van"
   }
        │
8. Dashboard auto-updates with new metrics
```

## HappyRobot Workflow Structure

```
Trigger: Web Call
    │
    └── Agent Node: Inbound Carrier Sales
            │
            ├── Prompt Node: System Instructions (Maya's behavior)
            │
            ├── Tool Node: verify_carrier
            │       Description: Verifies MC number eligibility
            │       Parameters: mc (string)
            │       └── Webhook: GET /api/verify_carrier?mc=@mc
            │
            ├── Tool Node: search_load
            │       Description: Searches loads by preferences
            │       Parameters: origin, destination, equipment_type
            │       └── Webhook: GET /api/loads (with params)
            │
            └── Tool Node: log_offer
                    Description: Logs call outcome and sentiment
                    Parameters: carrier_mc, negotiated_price, outcome,
                                sentiment, origin, destination, equipment_type
                    └── Webhook: POST /api/offers
```

## Data Models

### Load
| Field | Type | Description |
|-------|------|-------------|
| load_id | string | Unique identifier |
| origin | string | Pickup city |
| destination | string | Delivery city |
| equipment_type | string | Dry Van / Flatbed / Refrigerated |
| loadboard_rate | float | Listed rate |
| pickup_datetime | datetime | Pickup time |
| commodity_type | string | Type of goods |
| weight | float | Weight in lbs |
| miles | float | Distance |

### Offer (Call Log)
| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key |
| load_id | string | Load that was pitched |
| carrier_mc | string | Carrier MC number |
| negotiated_price | float | Final agreed or last offered price |
| outcome | string | agreed / not_agreed |
| sentiment | string | positive / neutral / negative |
| origin | string | Origin city from the call |
| destination | string | Destination city from the call |
| equipment_type | string | Equipment type from the call |
| timestamp | datetime | When the call ended |

## Negotiation Logic

```
Loadboard rate = $2500 (starting offer)

Round 1: Hold firm at $2500
Round 2: Concede to 97% → $2425
Round 3: Final offer at 95% → $2375 (floor)

If carrier pushes below $2375 → not_agreed
```

## Security

- All API endpoints require `X-API-Key` header
- HTTPS enforced on Railway (auto TLS)
- FMCSA_DEMO_MODE env var controls fallback for testing
- API key stored as Railway environment secret
