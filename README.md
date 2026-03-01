# Product Catalogue Microservice — Final Project

A RESTful Flask microservice for an eCommerce product catalogue,
complete with unit tests, integration tests, and BDD feature tests.

---

## Grading Task Index

| Task | File | Points |
|------|------|--------|
| Task 1 | [`tests/factories.py`](tests/factories.py) | 1 pt |
| Task 2 | [`tests/test_models.py`](tests/test_models.py) | 7 pts |
| Task 3 | [`tests/test_routes.py`](tests/test_routes.py) | 7 pts |
| Task 4 | [`service/routes.py`](service/routes.py) | 7 pts |
| Task 5 | [`features/steps/load_steps.py`](features/steps/load_steps.py) | 1 pt |
| Task 6 | [`features/products.feature`](features/products.feature) | 7 pts |
| Task 7 | [`features/steps/web_steps.py`](features/steps/web_steps.py) | 4 pts |

**Total: 34 points**

---

## Project Structure

```
product-catalogue/
│
├── service/
│   ├── __init__.py
│   ├── models.py            ← Product model, Category enum, SQLite persistence
│   └── routes.py            ← Flask REST API  ← Task 4
│
├── tests/
│   ├── __init__.py
│   ├── factories.py         ← Fake product generator  ← Task 1
│   ├── test_models.py       ← Model unit tests         ← Task 2
│   └── test_routes.py       ← Route integration tests  ← Task 3
│
├── features/
│   ├── environment.py       ← Behave hooks (start/stop server)
│   ├── products.feature     ← BDD scenarios            ← Task 6
│   └── steps/
│       ├── load_steps.py    ← Load test data           ← Task 5
│       └── web_steps.py     ← Step definitions         ← Task 7
│
├── .github/
│   └── workflows/
│       └── ci.yml           ← GitHub Actions CI pipeline
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Quick Start

### 1 — Clone and install
```bash
git clone https://github.com/<your-username>/product-catalogue.git
cd product-catalogue
pip install -r requirements.txt
```

### 2 — Run the API server
```bash
python -m service.routes
# → http://127.0.0.1:5000
```

### 3 — Run unit & integration tests (Tasks 2 & 3)
```bash
# All tests
python -m unittest discover tests -v

# Individual task files
python -m unittest tests/test_models.py -v   # Task 2
python -m unittest tests/test_routes.py -v  # Task 3
```

### 4 — Run BDD tests (Tasks 5, 6, 7)
```bash
behave features/products.feature
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/products` | List all products |
| GET | `/products?name=X` | Search by name |
| GET | `/products?category=X` | Search by category |
| GET | `/products?available=true` | Search by availability |
| GET | `/products?price=X` | Search by price |
| GET | `/products/<id>` | Get one product |
| POST | `/products` | Create a product |
| PUT | `/products/<id>` | Update a product |
| DELETE | `/products/<id>` | Delete a product |

### Valid categories
`UNKNOWN` · `CLOTHS` · `FOOD` · `HOUSEWARES` · `AUTOMOTIVE` · `TOOLS`

---

## Example curl commands

```bash
# Create
curl -X POST http://127.0.0.1:5000/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Hammer","description":"Claw hammer","price":"14.99","available":true,"category":"TOOLS"}'

# Read
curl http://127.0.0.1:5000/products/1

# Update
curl -X PUT http://127.0.0.1:5000/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Big Hammer","description":"20oz hammer","price":"24.99","available":true,"category":"TOOLS"}'

# Delete
curl -X DELETE http://127.0.0.1:5000/products/1

# Search by category
curl http://127.0.0.1:5000/products?category=FOOD

# Search by availability
curl http://127.0.0.1:5000/products?available=true
```

---

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — all 7 tasks complete"
git remote add origin https://github.com/<your-username>/product-catalogue.git
git push -u origin main
```

After pushing, GitHub Actions will automatically run all tests on every push.
