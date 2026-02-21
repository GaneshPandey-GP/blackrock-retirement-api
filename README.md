# blackrock-retirement-api

A production-grade REST API for automated retirement savings through expense-based micro-investments. Built for the BlackRock Hackathon 2026.

---

## Overview

This system implements an auto-saving strategy that rounds up expenses to the nearest ₹100 and invests the difference. It supports complex temporal constraints, financial transaction validation, and investment return calculations across NPS and Index Fund vehicles.

---

## Project Structure

```
BLACKROCK-HACKATHON-2026/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── transactions.py
│   │   ├── returns.py
│   │   └── performance.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── transaction_builder.py
│   │   ├── transaction_validator.py
│   │   ├── temporal_filter.py
│   │   ├── return_calculator.py
│   │   └── tax_calculator.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── performance_tracker.py
├── test/
│   ├── test_transactions.py
│   ├── test_returns.py
│   └── test_temporal_logic.py
├── Dockerfile
├── compose.yaml
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/blackrock/challenge/v1/transactions:parse` | Parse expenses and calculate ceiling & remanent |
| POST | `/blackrock/challenge/v1/transactions:validator` | Validate transactions (negatives, duplicates) |
| POST | `/blackrock/challenge/v1/transactions:filter` | Apply q, p, k period rules |
| POST | `/blackrock/challenge/v1/returns:nps` | Calculate NPS investment returns |
| POST | `/blackrock/challenge/v1/returns:index` | Calculate Index Fund investment returns |
| GET  | `/blackrock/challenge/v1/performance` | Get system performance metrics |

---

## Requirements

- Python 3.11+
- Docker
- pip

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/GaneshPandey-GP/blackrock-retirement-api.git
cd blackrock-retirement-api
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 5477 --reload
```

### 5. Access API docs

```
http://localhost:5477/docs
```

---

## Docker

### Build the image

```bash
docker build -t blk-hacking-ind-ganesh-pandey .
```

### Run the container

```bash
docker run -d -p 5477:5477 blk-hacking-ind-ganesh-pandey
```

### Using Docker Compose

```bash
docker compose -f compose.yaml up -d
```

---

## Testing

### Run all tests

```bash
pytest test/ -v
```

### Run specific test files

```bash
# Transaction tests
pytest test/test_transactions.py -v

# Temporal logic tests
pytest test/test_temporal_logic.py -v

# Returns tests
pytest test/test_returns.py -v
```

---

## Business Logic

### Auto-Saving Strategy

Each expense is rounded up to the next multiple of ₹100. The difference (remanent) is invested.

```
expense = ₹250  →  ceiling = ₹300  →  remanent = ₹50
```

### Period Rules

**q Periods (Fixed Override)**
- Replaces the remanent with a fixed amount during a date range
- If multiple q periods match, the one with the latest start date wins
- Applied before p periods

**p Periods (Extra Addition)**
- Adds an extra amount to the remanent during a date range
- All matching p periods are added together
- Applied after q periods

**k Periods (Grouping)**
- Groups transactions by date range for investment evaluation
- A transaction can belong to multiple k periods
- Each k period calculates its sum independently

### Processing Order

```
Step 1: Calculate ceiling and remanent
Step 2: Apply q period rules
Step 3: Apply p period rules
Step 4: Group by k periods
Step 5: Calculate returns
```

### Investment Options

| Instrument | Annual Rate | Constraints |
|------------|-------------|-------------|
| NPS (National Pension Scheme) | 7.11% | Tax rebate up to ₹2,00,000 |
| Index Fund (NIFTY 50) | 14.49% | None |

### Tax Slabs (Simplified)

| Income Range | Tax Rate |
|-------------|----------|
| ₹0 – ₹7,00,000 | 0% |
| ₹7,00,001 – ₹10,00,000 | 10% on amount above ₹7L |
| ₹10,00,001 – ₹12,00,000 | 15% on amount above ₹10L |
| ₹12,00,001 – ₹15,00,000 | 20% on amount above ₹12L |
| Above ₹15,00,000 | 30% on amount above ₹15L |

### Compound Interest Formula

```
A = P × (1 + r/n)^(n×t)
```

Where:
- `A` = Final amount
- `P` = Principal (remanent invested)
- `r` = Annual interest rate
- `n` = Compounding frequency (annually = 1)
- `t` = Years until age 60 (min 5 years)

### Inflation Adjustment

```
A_real = A / (1 + inflation)^t
```

---

## Example Request

### Parse Transactions

```bash
curl -X POST "http://localhost:5477/blackrock/challenge/v1/transactions:parse" \
  -H "Content-Type: application/json" \
  -d '[
    {"date": "2023-10-12 20:15:30", "amount": 250},
    {"date": "2023-02-28 15:49:20", "amount": 375},
    {"date": "2023-07-01 21:59:00", "amount": 620},
    {"date": "2023-12-17 08:09:45", "amount": 480}
  ]'
```

### Returns Calculation (NPS)

```bash
curl -X POST "http://localhost:5477/blackrock/challenge/v1/returns:nps" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 29,
    "wage": 50000,
    "inflation": 5.5,
    "q": [{"fixed": 0, "start": "2023-07-01 00:00:00", "end": "2023-07-31 23:59:59"}],
    "p": [{"extra": 25, "start": "2023-10-01 08:00:00", "end": "2023-12-31 19:59:59"}],
    "k": [
      {"start": "2023-01-01 00:00:00", "end": "2023-12-31 23:59:59"},
      {"start": "2023-03-01 00:00:00", "end": "2023-11-30 23:59:59"}
    ],
    "transactions": [
      {"date": "2023-02-28 15:49:20", "amount": 375},
      {"date": "2023-07-01 21:59:00", "amount": 620},
      {"date": "2023-10-12 20:15:30", "amount": 250},
      {"date": "2023-12-17 08:09:45", "amount": 480}
    ]
  }'
```

---

## Dependencies

```
fastapi
uvicorn
pydantic
psutil
pytest
pytest-asyncio
```

---

## Validation Rules

- Negative amounts are rejected
- Duplicate transactions (same date + same amount) are rejected
- Amount must be less than ₹5,00,000
- Timestamps must follow format: `YYYY-MM-DD HH:mm:ss`
- All dates must be within the same calendar year

---

## Performance Endpoint

```bash
curl http://localhost:5477/blackrock/challenge/v1/performance
```

Response:
```json
{
  "time": "00:00:11.135",
  "memory": "25.11 MB",
  "threads": 16
}
```# blackrock-retirement-api

A production-grade REST API for automated retirement savings through expense-based micro-investments. Built for the BlackRock Hackathon 2026.

---

## Overview

This system implements an auto-saving strategy that rounds up expenses to the nearest ₹100 and invests the difference. It supports complex temporal constraints, financial transaction validation, and investment return calculations across NPS and Index Fund vehicles.

---

## Project Structure

```
BLACKROCK-HACKATHON-2026/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── transactions.py
│   │   ├── returns.py
│   │   └── performance.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── transaction_builder.py
│   │   ├── transaction_validator.py
│   │   ├── temporal_filter.py
│   │   ├── return_calculator.py
│   │   └── tax_calculator.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── date_utils.py
│   │   ├── math_utils.py
│   │   └── performance_tracker.py
│   └── core/
│       ├── __init__.py
│       └── config.py
├── test/
│   ├── test_transactions.py
│   ├── test_returns.py
│   └── test_temporal_logic.py
├── Dockerfile
├── compose.yaml
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/blackrock/challenge/v1/transactions:parse` | Parse expenses and calculate ceiling & remanent |
| POST | `/blackrock/challenge/v1/transactions:validator` | Validate transactions (negatives, duplicates) |
| POST | `/blackrock/challenge/v1/transactions:filter` | Apply q, p, k period rules |
| POST | `/blackrock/challenge/v1/returns:nps` | Calculate NPS investment returns |
| POST | `/blackrock/challenge/v1/returns:index` | Calculate Index Fund investment returns |
| GET  | `/blackrock/challenge/v1/performance` | Get system performance metrics |

---

## Requirements

- Python 3.11+
- Docker
- pip

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/{your-username}/blackrock-retirement-api.git
cd blackrock-retirement-api
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5477 --reload
```

### 5. Access API docs

```
http://localhost:5477/docs
```

---

## Docker

### Build the image

```bash
docker build -t blk-hacking-ind-{name-lastname} .
```

### Run the container

```bash
docker run -d -p 5477:5477 blk-hacking-ind-{name-lastname}
```

### Using Docker Compose

```bash
docker compose -f compose.yaml up -d
```

---

## Testing

### Run all tests

```bash
pytest test/ -v
```

### Run specific test files

```bash
# Transaction tests
pytest test/test_transactions.py -v

# Temporal logic tests
pytest test/test_temporal_logic.py -v

# Returns tests
pytest test/test_returns.py -v
```

---

## Business Logic

### Auto-Saving Strategy

Each expense is rounded up to the next multiple of ₹100. The difference (remanent) is invested.

```
expense = ₹250  →  ceiling = ₹300  →  remanent = ₹50
```

### Period Rules

**q Periods (Fixed Override)**
- Replaces the remanent with a fixed amount during a date range
- If multiple q periods match, the one with the latest start date wins
- Applied before p periods

**p Periods (Extra Addition)**
- Adds an extra amount to the remanent during a date range
- All matching p periods are added together
- Applied after q periods

**k Periods (Grouping)**
- Groups transactions by date range for investment evaluation
- A transaction can belong to multiple k periods
- Each k period calculates its sum independently

### Processing Order

```
Step 1: Calculate ceiling and remanent
Step 2: Apply q period rules
Step 3: Apply p period rules
Step 4: Group by k periods
Step 5: Calculate returns
```

### Investment Options

| Instrument | Annual Rate | Constraints |
|------------|-------------|-------------|
| NPS (National Pension Scheme) | 7.11% | Tax rebate up to ₹2,00,000 |
| Index Fund (NIFTY 50) | 14.49% | None |

### Tax Slabs (Simplified)

| Income Range | Tax Rate |
|-------------|----------|
| ₹0 – ₹7,00,000 | 0% |
| ₹7,00,001 – ₹10,00,000 | 10% on amount above ₹7L |
| ₹10,00,001 – ₹12,00,000 | 15% on amount above ₹10L |
| ₹12,00,001 – ₹15,00,000 | 20% on amount above ₹12L |
| Above ₹15,00,000 | 30% on amount above ₹15L |

### Compound Interest Formula

```
A = P × (1 + r/n)^(n×t)
```

Where:
- `A` = Final amount
- `P` = Principal (remanent invested)
- `r` = Annual interest rate
- `n` = Compounding frequency (annually = 1)
- `t` = Years until age 60 (min 5 years)

### Inflation Adjustment

```
A_real = A / (1 + inflation)^t
```

---

## Example Request

### Parse Transactions

```bash
curl -X POST "http://localhost:5477/blackrock/challenge/v1/transactions:parse" \
  -H "Content-Type: application/json" \
  -d '[
    {"date": "2023-10-12 20:15:30", "amount": 250},
    {"date": "2023-02-28 15:49:20", "amount": 375},
    {"date": "2023-07-01 21:59:00", "amount": 620},
    {"date": "2023-12-17 08:09:45", "amount": 480}
  ]'
```

### Returns Calculation (NPS)

```bash
curl -X POST "http://localhost:5477/blackrock/challenge/v1/returns:nps" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 29,
    "wage": 50000,
    "inflation": 5.5,
    "q": [{"fixed": 0, "start": "2023-07-01 00:00:00", "end": "2023-07-31 23:59:59"}],
    "p": [{"extra": 25, "start": "2023-10-01 08:00:00", "end": "2023-12-31 19:59:59"}],
    "k": [
      {"start": "2023-01-01 00:00:00", "end": "2023-12-31 23:59:59"},
      {"start": "2023-03-01 00:00:00", "end": "2023-11-30 23:59:59"}
    ],
    "transactions": [
      {"date": "2023-02-28 15:49:20", "amount": 375},
      {"date": "2023-07-01 21:59:00", "amount": 620},
      {"date": "2023-10-12 20:15:30", "amount": 250},
      {"date": "2023-12-17 08:09:45", "amount": 480}
    ]
  }'
```

---

## Dependencies

```
fastapi
uvicorn
pydantic
psutil
pytest
pytest-asyncio
```

---

## Validation Rules

- Negative amounts are rejected
- Duplicate transactions (same date + same amount) are rejected
- Amount must be less than ₹5,00,000
- Timestamps must follow format: `YYYY-MM-DD HH:mm:ss`
- All dates must be within the same calendar year

---

## Performance Endpoint

```bash
curl http://localhost:5477/blackrock/challenge/v1/performance
```

Response:
```json
{
  "time": "00:00:11.135",
  "memory": "25.11 MB",
  "threads": 16
}
```
