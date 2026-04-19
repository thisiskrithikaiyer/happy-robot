# System Architecture & Data Flow

## What is the API Key?

The API key (`cdc33e44d693a3a58451898d4ec9df862c65b954`) is a **security token** that:
- Authenticates all requests to the API
- Prevents unauthorized access
- Required in the `X-API-Key` header for every request
- In production, rotate keys and use environment variables

## How Does Everything Connect?

### 1️⃣ Components

```
┌─────────────────────────────────────────────┐
│         HappyRobot Platform                 │
│  (Voice AI Agent - Inbound Calls)           │
└────────────────────┬────────────────────────┘
                     │ (HTTP Requests with API Key)
                     │
        ┌────────────▼─────────────┐
        │   Flask API Server       │
        │  (http://localhost:5000) │
        │                          │
        │  - Verify Carriers       │
        │  - Search Loads          │
        │  - Log Outcomes          │
        │  - Serve Metrics         │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │   SQLite Database         │
        │                           │
        │  Loads Table (15 records) │
        │  Offers Table (call logs) │
        └────────────────────────────┘
                     ▲
                     │
        ┌────────────┴──────────────┐
        │   Next.js Dashboard       │
        │ (http://localhost:3000)   │
        │                           │
        │ - Fetches /api/metrics    │
        │ - Shows charts & stats    │
        │ - Auto-refreshes every 5s │
        └───────────────────────────┘
```

### 2️⃣ Data Flow: Inbound Call Example

```
Step 1: Carrier calls in
  Carrier → HappyRobot Web Trigger → Agent answers

Step 2: Verification
  Agent: "What's your MC number?"
  Carrier: "MC123456"
  Agent calls: GET /api/verify_carrier?mc=MC123456 {X-API-Key: ...}
  API Response: {"eligible": true}

Step 3: Load Search
  Agent: "What origin and destination?"
  Carrier: "LA to NY, Dry Van"
  Agent calls: GET /api/loads?origin=LA&destination=NY&equipment_type=Dry Van
  API Response: [
    {
      "load_id": "L001",
      "loadboard_rate": 2500,
      ...other fields...
    }
  ]

Step 4: Negotiation
  Agent: "We have a load from LA to NY for $2500. Interested?"
  Carrier: "Can you do $2100?"
  
  Agent Logic:
    - $2100 < $2500 (loadboard_rate)
    - Counter with: $2500 * 0.95 = $2375
    - Agent: "Best I can do is $2375"
  
  Carrier: "Ok, I'll do $2350"
  
  Agent Logic:
    - $2350 >= $2375? No, but close
    - Accept and prepare to log as "agreed"

Step 5: Log Outcome
  Agent calls: POST /api/offers {
    "load_id": "L001",
    "carrier_mc": "MC123456",
    "negotiated_price": 2350,
    "outcome": "agreed",
    "sentiment": "positive"
  }
  API Response: {"message": "Offer logged"}
  Database: INSERT INTO offers (...)

Step 6: Dashboard Auto-Updates
  Browser fetches: GET /api/metrics {X-API-Key: ...}
  API aggregates from database:
  - total_calls: 1
  - success_rate: 100%
  - avg_negotiated_price: 2350
  - sentiment: {"positive": 1}
  - outcomes: {"agreed": 1}
  
  Dashboard renders charts and stats
```

## 3️⃣ How API Becomes "Tools" in HappyRobot

HappyRobot has a **Tool Use** feature that lets agents call external APIs. You configure:

```
Tool 1: Verify Carrier Eligibility
├─ Type: HTTP GET
├─ URL: https://api.example.com/api/verify_carrier
├─ Params: mc (from carrier input)
├─ Headers: X-API-Key
└─ Output: Boolean (eligible or not)

Tool 2: Search Available Loads
├─ Type: HTTP GET
├─ URL: https://api.example.com/api/loads
├─ Params: origin, destination, equipment_type
├─ Headers: X-API-Key
└─ Output: Array of load objects

Tool 3: Log Call Outcome
├─ Type: HTTP POST
├─ URL: https://api.example.com/api/offers
├─ Body: JSON with load_id, carrier_mc, price, outcome, sentiment
├─ Headers: X-API-Key, Content-Type
└─ Output: {"message": "Offer logged"}

Tool 4: Get Real-Time Metrics
├─ Type: HTTP GET
├─ URL: https://api.example.com/api/metrics
├─ Headers: X-API-Key
└─ Output: Aggregated call statistics
```

In the HappyRobot workflow, you write conversation logic like:
```
WHEN carrier_says_something:
  IF "interested" in response:
    CALL Tool: SearchLoads(...)
    GET loads_list
    FOR each load:
      PRESENT load details
      WAIT for response
  ELIF "what's your best price" in response:
    counter_price = loadboard_rate * 0.95
    RESPOND: "I can do ${counter_price}"
```

## 4️⃣ Key Concepts

| Concept | Definition | Example |
|---------|-----------|---------|
| **API Key** | Security token | `cdc33e44d693a3a58451898d4ec9df862c65b954` |
| **Loadboard Rate** | Listed rate for a load | `$2500` |
| **Negotiation Range** | Acceptable price bounds | `$2100 - $2500` (80-100% of rate) |
| **Outcome** | Call result | `"agreed"` or `"not_agreed"` |
| **Sentiment** | Carrier tone analysis | `"positive"`, `"negative"`, `"neutral"` |
| **Tool Call** | Agent invoking API | `GET /api/verify_carrier` |
| **Metric** | Aggregated stat | `success_rate: 0.67` |

## 5️⃣ Data Storage & Aggregation

```
SQLite Database
│
├─ Load Table
│  ├─ load_id (PK)
│  ├─ origin
│  ├─ destination
│  ├─ equipment_type
│  ├─ loadboard_rate
│  └─ ... (other fields)
│
└─ Offer Table
   ├─ id (PK)
   ├─ load_id (FK)
   ├─ carrier_mc
   ├─ negotiated_price
   ├─ outcome
   ├─ sentiment
   └─ timestamp

Metrics Computation (GET /api/metrics):
├─ total_calls = COUNT(*) FROM Offer
├─ agreed = COUNT(*) WHERE outcome='agreed'
├─ success_rate = agreed / total_calls
├─ avg_price = AVG(negotiated_price) FROM Offer
├─ sentiment = GROUP_BY(sentiment) COUNT
├─ outcomes = GROUP_BY(outcome) COUNT
└─ top_loads = GROUP_BY(load_id) LIMIT 5
```

## 6️⃣ API Authentication Flow

```
Every Request:
│
├─ Client prepares HTTP request
├─ Adds header: "X-API-Key: cdc33e44d693a3a58451898d4ec9df862c65b954"
├─ Sends to: /api/endpoint
│
└─ Server:
   ├─ Reads X-API-Key header
   ├─ Compares with Config.API_KEY
   ├─ IF match: ✅ Process request
   └─ IF NO match: ❌ Return 401 Unauthorized
```

## 7️⃣ Full Lifecycle Example

1. **Monday 9 AM**: Carrier MC123 calls in
2. Agent verifies MC (calls FMCSA API)
3. Agent asks preferences, searches loads
4. Agent pitches L001: "LA→NY Dry Van $2500"
5. Carrier counters: "$2200"
6. Agent counter: "$2375"
7. Carrier accepts: "$2350"
8. Agent logs to database:
   ```json
   {
     "load_id": "L001",
     "carrier_mc": "MC123",
     "negotiated_price": 2350,
     "outcome": "agreed",
     "sentiment": "positive",
     "timestamp": "2026-04-18T09:15:00"
   }
   ```
9. Dashboard updates:
   - Total calls: 1
   - Success rate: 100%
   - Avg price: $2350
   - Metrics visible in real-time charts

## 8️⃣ Why This Architecture?

✅ **Separation of Concerns**: API handles data; HappyRobot handles conversation  
✅ **Scalability**: Easy to add more loads, carriers, or metrics  
✅ **Security**: API key prevents unauthorized access  
✅ **Auditability**: All calls logged for compliance  
✅ **Observability**: Dashboard shows performance in real-time  
✅ **Extensibility**: Easy to add new API endpoints or tools