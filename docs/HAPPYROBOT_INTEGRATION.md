# HappyRobot + API Integration Guide

## Architecture Overview

The HappyRobot AI agent interacts with the Loads API to automate inbound carrier calls. The API serves as the "external tools" that the agent can invoke during conversations.

```
┌─────────────────────────────────────────────────────────────└
│ Carrier Calls Web Trigger                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  HappyRobot AI Agent       │
        │ (Voice Conversation)       │
        │                            │
        │  - Verify MC (FMCSA)      │
        │  - Search Loads            │
        │  - Negotiate Price         │
        │  - Log Outcome             │
        └────────────┬───────────────┘
                     │
        ┌────────────▼───────────────┐
        │   Loads API (Tools)        │
        │                            │
        │  GET /api/loads            │
        │  GET /api/verify_carrier   │
        │  POST /api/offers          │
        │  GET /api/metrics          │
        └────────────┬───────────────┘
                     │
        ┌────────────▼───────────────┐
        │  SQLite Database           │
        │  Loads & Offers Table      │
        └────────────────────────────┘
```

## Agent Workflow: Call Lifecycle

### 1. **Inbound Call Received**
   - Carrier calls via HappyRobot web call trigger
   - Agent answers with greeting

### 2. **Verification Step**
   **Tool Call:** `GET /api/verify_carrier?mc=<MC_NUMBER>`
   ```json
   {
     "eligible": true
   }
   ```
   - Agent asks for MC number
   - Calls FMCSA API validation endpoint
   - If not eligible, agent ends call

### 3. **Load Search & Pitch**
   **Tool Call:** `GET /api/loads?origin=<origin>&destination=<destination>&equipment_type=<type>`
   ```json
   [
     {
       "load_id": "L001",
       "origin": "Los Angeles, CA",
       "destination": "New York, NY",
       "pickup_datetime": "2026-04-19T...",
       "equipment_type": "Dry Van",
       "loadboard_rate": 2500.0,
       ...
     }
   ]
   ```
   - Agent asks carrier about preferences (origin, destination, equipment)
   - Calls loads search endpoint
   - Pitches best matching load with details

### 4. **Negotiation (Up to 3 Rounds)**
   Based on carrier's response:
   
   **Round 1: Pitch**
   - Agent: "Load available at $2500 loadboard rate"
   
   **Round 2: Carrier Counter-Offer**
   - Carrier: "Can you do $2200?"
   - Agent Logic: $2200 < $2500 (loadboard_rate)
     - Counter: "Best I can do is $2375 (95% of $2500)"
   
   **Round 3: Final Negotiation**
   - Carrier: "What about $2300?"
   - Agent Logic: $2300 < $2375
     - Counter: "Can do $2350, final offer"
   
   **Agreement Check**
   - If carrier accepts ≥ $2350 → **Proceed to Logging**
   - If carrier declines → **Log as not_agreed**

### 5. **Outcome Logging**
   **Tool Call:** `POST /api/offers`
   ```json
   {
     "load_id": "L001",
     "carrier_mc": "MC123456",
     "negotiated_price": 2350.0,
     "outcome": "agreed",  // or "not_agreed"
     "sentiment": "positive"  // or "neutral", "negative"
   }
   ```
   - Agent extracts: agreed price, carrier info, sentiment analysis
   - Posts to outcomes logging endpoint
   - Database records the call

### 6. **Transfer to Sales Rep** (Mocked)
   - Agent: "Great! I'm transferring you to our sales team to finalize..."
   - Mock endpoint confirms transfer success
   - Call ends (web-based, actual transfer not required)

## Setting Up Agent in HappyRobot

### Step 1: Create Workflow
1. Log into HappyRobot platform
2. Create new workflow named "Inbound Carrier Sales"
3. Set trigger: Web call

### Step 2: Add Tool Integrations
In the workflow builder, add these tool calls:

#### Tool 1: Verify Carrier
```
Name: "Verify Carrier Eligibility"
Type: HTTP Request
Method: GET
URL: https://YOUR_API_URL/api/verify_carrier
Headers: 
  - X-API-Key: YOUR_API_KEY
  - Content-Type: application/json
Parameters: 
  - mc: {mc_number_from_carrier}
Expected Output: { "eligible": true/false }
```

#### Tool 2: Search Loads
```
Name: "Find Available Loads"
Type: HTTP Request
Method: GET
URL: https://YOUR_API_URL/api/loads
Headers:
  - X-API-Key: YOUR_API_KEY
Parameters:
  - origin: {carrier_origin_preference}
  - destination: {carrier_destination_preference}
  - equipment_type: {equipment_needed}
Expected Output: Array of loads with fields
```

#### Tool 3: Log Offer
```
Name: "Log Call Outcome"
Type: HTTP Request
Method: POST
URL: https://YOUR_API_URL/api/offers
Headers:
  - X-API-Key: YOUR_API_KEY
  - Content-Type: application/json
Body:
{
  "load_id": {selected_load_id},
  "carrier_mc": {carrier_mc_number},
  "negotiated_price": {final_price},
  "outcome": {agreed|not_agreed},
  "sentiment": {positive|negative|neutral}
}
Expected Output: { "message": "Offer logged" }
```

### Step 3: Define Agent Conversation Logic

**Pseudocode in HappyRobot:**
```
FUNCTION InboundCarrierSales():
    
    // Welcome
    SPEAK("Welcome to [Company]. What's your MC number?")
    mc_number = LISTEN()
    
    // Verify
    is_eligible = CALL_TOOL(VerifyCarrier, mc=mc_number)
    IF NOT is_eligible:
        SPEAK("Sorry, you're not eligible to work with us.")
        END_CALL()
    
    // Preferences
    SPEAK("What origin and destination are you interested in?")
    origin = LISTEN()
    destination = LISTEN()
    
    SPEAK("What equipment type do you need?")
    equipment_type = LISTEN()
    
    // Search Loads
    loads = CALL_TOOL(SearchLoads, origin, destination, equipment_type)
    IF EMPTY(loads):
        SPEAK("No loads available matching your criteria.")
        END_CALL()
    
    best_load = loads[0]
    loadboard_rate = best_load.loadboard_rate
    
    // Pitch
    SPEAK(`Load available: ${best_load.origin} to ${best_load.destination}. 
           ${best_load.commodity_type}, ${best_load.weight} lbs. 
           Rate: $${loadboard_rate}. Interested?`)
    response = LISTEN()
    
    negotiated_price = loadboard_rate
    round_count = 0
    
    // Negotiation Loop (max 3 rounds)
    WHILE round_count < 3:
        IF "yes" IN response.lower() AND price >= loadboard_rate * 0.90:
            BREAK  // Agreement reached
        
        IF contains_price_offer(response):
            offered_price = extract_price(response)
            negotiated_price = MAX(offered_price, loadboard_rate * 0.95)
            
            IF offered_price >= negotiated_price:
                SPEAK("Deal! At $${negotiated_price}.")
                BREAK
            ELSE:
                counter_price = negotiated_price
                SPEAK("I can go down to $${counter_price}. Can you work with that?")
                response = LISTEN()
                round_count += 1
    
    // Log the outcome
    outcome = "agreed" if price >= loadboard_rate * 0.90 else "not_agreed"
    sentiment = analyze_sentiment(response)
    
    CALL_TOOL(LogOffer,
        load_id=best_load.load_id,
        carrier_mc=mc_number,
        negotiated_price=negotiated_price,
        outcome=outcome,
        sentiment=sentiment
    )
    
    IF outcome == "agreed":
        SPEAK("Excellent! I'm transferring you to our sales team to finalize.")
    ELSE:
        SPEAK("Thanks for your time. Feel free to call back anytime.")
    
    END_CALL()
```

## Key Concepts

### API Key Security
- All endpoints require `X-API-Key` header
- Key is shared between HappyRobot and API
- In production, use environment variables and rotate keys

### Negotiation Logic
- **Loadboard Rate**: The listed rate for a load
- **Acceptance Threshold**: Carrier offer must be ≥ 90% of loadboard_rate
- **Counter-Offer**: API suggests 95% of loadboard_rate
- **Max Rounds**: 3 back-and-forths to prevent infinite loops

### Data Classification
- **Outcome**: "agreed" or "not_agreed" (deterministic)
- **Sentiment**: "positive", "negative", "neutral" (AI-analyzed from carrier tone/words)
- **Metrics**: Automatically aggregated for dashboard

## Testing the Integration

### 1. Test Carrier Verification
```bash
curl -H "X-API-Key: YOUR_KEY" \
  "http://localhost:5000/api/verify_carrier?mc=MC123456"
```

### 2. Test Load Search
```bash
curl -H "X-API-Key: YOUR_KEY" \
  "http://localhost:5000/api/loads?origin=LA&destination=NY"
```

### 3. Test Logging an Offer
```bash
curl -X POST -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"load_id":"L001","carrier_mc":"MC123","negotiated_price":2300,"outcome":"agreed","sentiment":"positive"}' \
  http://localhost:5000/api/offers
```

### 4. Check Metrics
```bash
curl -H "X-API-Key: YOUR_KEY" \
  http://localhost:5000/api/metrics
```

## Deployment Checklist

- [ ] Deploy API to cloud (Fly.io, AWS, etc.)
- [ ] Update HappyRobot tool URLs to deployed API
- [ ] Configure HTTPS with valid SSL certificates
- [ ] Set environment variables (API_KEY, DATABASE_URL, FMCSA_KEY)
- [ ] Test all tool calls from HappyRobot workflow
- [ ] Deploy dashboard to show metrics
- [ ] Monitor metrics dashboard for call volume and success rates
- [ ] Log all calls for compliance and analysis