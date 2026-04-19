# Inbound Carrier Sales Automation POC for Acme Logistics

## Overview
This proof of concept demonstrates an automated inbound carrier sales system built on the HappyRobot platform. The AI agent handles carrier calls, vets eligibility, matches loads, negotiates pricing, and logs outcomes for analysis.

## Technical Implementation

### HappyRobot Agent Workflow
- **Inbound Call Handling**: Receives calls from carriers via web call trigger.
- **Eligibility Verification**: Asks for MC number and verifies using FMCSA API.
- **Load Matching**: Searches available loads via custom API based on carrier preferences.
- **Negotiation Logic**: Pitches load details, accepts counteroffers >= loadboard_rate, otherwise counters with 5% discount, up to 3 rounds.
- **Outcome Processing**: Logs agreed price, outcome (agreed/not_agreed), sentiment (positive/negative/neutral).
- **Transfer Simulation**: Mocks transfer to sales rep upon agreement.

### Supporting API
- **Endpoints**:
  - GET /api/loads: Search loads with filters (origin, destination, equipment_type).
  - POST /api/offers: Log call outcomes.
  - GET /api/metrics: Retrieve dashboard metrics.
  - GET /api/verify_carrier: Verify MC eligibility.
- **Security**: API key authentication on all endpoints.
- **Database**: SQLite with Load and Offer models.

### Metrics Dashboard
- **Metrics Tracked**:
  - Total calls
  - Success rate (agreed calls / total)
  - Average negotiated price
  - Sentiment distribution (pie chart)
  - Outcome counts (bar chart)
- **Technology**: HTML/JS with Chart.js for visualizations.

### Deployment
- **Containerization**: Docker with separate containers for API and dashboard.
- **Cloud Deployment**: Ready for Fly.io or similar with HTTPS and API key auth.
- **Local Setup**: docker-compose for development.

## Benefits for Acme Logistics
- Automates repetitive inbound sales tasks.
- Reduces cost per lead through AI-driven negotiations.
- Provides real-time insights via custom dashboard.
- Scales with enterprise needs.

## Next Steps
- Deploy to production cloud environment.
- Integrate with existing CRM systems.
- Expand negotiation logic based on historical data.

For access to the deployed dashboard and code repository, see the provided links.