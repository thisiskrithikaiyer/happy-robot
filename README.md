# HappyRobot Inbound Carrier Sales POC

A proof-of-concept for automating inbound carrier load sales using HappyRobot AI agents, featuring real-time negotiation, FMCSA verification, and a professional metrics dashboard.

## 📋 Project Structure

```
happy-robot/
├── api/                          # Flask REST API
│   ├── app.py                    # Main Flask app
│   ├── models.py                 # SQLAlchemy models (Load, Offer)
│   ├── routes.py                 # API endpoints
│   ├── config.py                 # Configuration
│   ├── utils.py                  # FMCSA verification
│   ├── requirements.txt           # Python dependencies
│   └── create_sample_data.py      # Seed database with loads
│
├── dashboard/                    # Next.js Metrics Dashboard
│   ├── pages/                    # Next.js pages
│   │   ├── _app.js              # App wrapper
│   │   └── index.js             # Main dashboard
│   ├── components/               # React components
│   │   ├── MetricCard.js        # Metric display card
│   │   └── ChartsSection.js     # Charts (Recharts)
│   ├── package.json              # Node dependencies
│   ├── tailwind.config.js        # Tailwind CSS config
│   ├── .env.example              # Environment template
│   └── README.md                 # Dashboard setup guide
│
├── docker/                       # Docker files
│   ├── Dockerfile.api           # API container
│   └── Dockerfile.dashboard     # Dashboard container
│
├── docs/                         # Documentation
│   ├── email_draft.md           # Email to Carlos Becker
│   ├── build_description.md     # For Acme Logistics
│   └── HAPPYROBOT_INTEGRATION.md # Integration guide
│
├── docker-compose.yml            # Local dev setup
├── .env                          # Environment variables
└── happyrobot_api.postman_collection.json  # Postman collection
```

## 🚀 Quick Start

### 1. Start the API

```bash
cd api
pip3 install -r requirements.txt
python3 app.py
```

API will run on `http://127.0.0.1:5000`

### 2. Start the Dashboard (Choose One)

#### Option A: Simple HTTP Server (Quick)
```bash
cd dashboard
python3 -m http.server 8080
# Visit http://localhost:8080/index.html
```

#### Option B: Next.js Dev Server (Recommended)
```bash
cd dashboard
npm install
npm run dev
# Visit http://localhost:3000
```

### 3. Create Sample Data
The database is auto-initialized. Visit `http://127.0.0.1:5000/api/loads` to verify loads are populated.

## 🔌 API Endpoints

All endpoints require `X-API-Key: cdc33e44d693a3a58451898d4ec9df862c65b954` header.

### Get Loads
```bash
GET /api/loads?origin=LA&destination=NY&equipment_type=Dry Van
```
Returns array of available loads matching filters.

### Verify Carrier
```bash
GET /api/verify_carrier?mc=MC123456
```
Returns `{ "eligible": true/false }` based on FMCSA API.

### Log Offer
```bash
POST /api/offers
Content-Type: application/json
X-API-Key: YOUR_KEY

{
  "load_id": "L001",
  "carrier_mc": "MC123456",
  "negotiated_price": 2300.0,
  "outcome": "agreed",
  "sentiment": "positive"
}
```

### Get Metrics
```bash
GET /api/metrics
```
Returns aggregated metrics:
- `total_calls`: Total inbound calls
- `success_rate`: % of calls that resulted in agreement
- `avg_negotiated_price`: Average final negotiated price
- `unique_carriers`: Number of unique carriers called
- `sentiment`: Breakdown of positive/negative/neutral
- `outcomes`: Count of agreed vs not_agreed
- `top_loads`: Most frequently pitched loads

## 🤖 HappyRobot Integration

The API acts as **external tools** that HappyRobot AI agents can invoke during conversations. See [HAPPYROBOT_INTEGRATION.md](docs/HAPPYROBOT_INTEGRATION.md) for detailed setup.

### Agent Workflow
1. **Verify**: Agent calls `/api/verify_carrier` to check MC eligibility
2. **Search**: Agent calls `/api/loads` to find matching loads based on carrier preferences
3. **Negotiate**: Agent uses logic to handle up to 3 rounds of counter-offers
4. **Log**: Agent calls `/api/offers` to record outcome and sentiment

### Setting Up in HappyRobot
1. Create inbound workflow with web call trigger
2. Add HTTP tool calls for each endpoint
3. Configure agent conversation logic for negotiation
4. Test with web call simulator

## 📊 Dashboard Metrics

The dashboard auto-refreshes every 5 seconds and displays:

**Key Metrics**
- 📞 Total Calls
- ✅ Success Rate (% agreed)
- 💰 Avg Negotiated Price
- 🤝 Agreed Deals

**Charts**
- 🍰 **Sentiment Distribution**: Pie chart showing positive/negative/neutral carrier sentiment
- 📊 **Outcomes**: Bar chart comparing agreed vs not_agreed calls

**Tables**
- **Outcomes Breakdown**: Count of agreed and not_agreed
- **Sentiment Breakdown**: Count by sentiment type
- **Top Loads**: Most frequently pitched loads

## 🧪 Testing with Postman

Import the included Postman collection:
1. Open Postman
2. Click "Import"
3. Select `happyrobot_api.postman_collection.json`
4. API key is pre-configured
5. Send requests and verify responses

Or use curl:
```bash
# Get loads
curl -H "X-API-Key: cdc33e44d693a3a58451898d4ec9df862c65b954" \
  http://127.0.0.1:5000/api/loads

# Log an offer
curl -X POST -H "X-API-Key: cdc33e44d693a3a58451898d4ec9df862c65b954" \
  -H "Content-Type: application/json" \
  -d '{"load_id":"L001","carrier_mc":"MC123","negotiated_price":2300,"outcome":"agreed","sentiment":"positive"}' \
  http://127.0.0.1:5000/api/offers
```

## 🐳 Docker Deployment (Local)

```bash
docker compose up -d
```

Services:
- **API**: http://localhost:5000
- **Dashboard**: http://localhost:8080

## ☁️ Cloud Deployment

### Deploy to Fly.io

1. **Install Fly CLI**: https://fly.io/docs/hands-on/install-flyctl/

2. **Create Fly app for API**:
```bash
cd api
flyctl launch
# Name: happy-robot-api
# Dockerfile: No (use flyctl's default)
```

3. **Set environment variables**:
```bash
flyctl secrets set API_KEY=cdc33e44d693a3a58451898d4ec9df862c65b954
flyctl secrets set FMCSA_KEY=cdc33e44d693a3a58451898d4ec9df862c65b954
flyctl secrets set DATABASE_URL=file:/app/instance/happyrobot.db
```

4. **Deploy**:
```bash
flyctl deploy
```

5. **Deploy Dashboard** (similar steps for dashboard folder)

6. **Update Dashboard Config**: Set `NEXT_PUBLIC_API_URL` to deployed API URL

## 📝 Deliverables

- ✅ Email draft to Carlos Becker: [docs/email_draft.md](docs/email_draft.md)
- ✅ Build description for Acme Logistics: [docs/build_description.md](docs/build_description.md)
- ✅ HappyRobot integration guide: [docs/HAPPYROBOT_INTEGRATION.md](docs/HAPPYROBOT_INTEGRATION.md)
- ✅ Postman collection: [happyrobot_api.postman_collection.json](happyrobot_api.postman_collection.json)
- ✅ Dashboard accessible at http://localhost:3000 (or 8080 for static version)
- ✅ API documentation and code repository
- 📹 Video demo: (Record walkthrough of setup, demo, and metrics)

## 🔐 Security

- All API endpoints require `X-API-Key` header authentication
- In production, use HTTPS (Fly.io provides automatic HTTPS)
- Store secrets in environment variables, never in code
- Rotate API keys regularly

## 📈 Metrics Example

After logging a few test offers:
```json
{
  "total_calls": 3,
  "success_rate": 0.67,
  "avg_negotiated_price": 2050.0,
  "unique_carriers": 2,
  "sentiment": {
    "positive": 1,
    "negative": 1,
    "neutral": 1
  },
  "outcomes": {
    "agreed": 2,
    "not_agreed": 1
  },
  "top_loads": [
    {"load_id": "L001", "calls": 2}
  ]
}
```

## 🤝 Support

For questions about HappyRobot integration, see [HAPPYROBOT_INTEGRATION.md](docs/HAPPYROBOT_INTEGRATION.md).

For API issues, check the API logs:
```bash
# View running API
lsof -i :5000
```

## 📄 License

This is a proof-of-concept for FDE Technical Challenge.