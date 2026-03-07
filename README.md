# web_services_coursework

# Travel Without Barriers API

## Project Overview

Travel Without Barriers is a RESTful backend API designed to help people who face **financial or mental health barriers to travel** discover destinations that are easier and less stressful to plan.

Many people want to travel but feel overwhelmed by factors such as:

- high travel costs
- overcrowded tourist destinations
- difficulty planning trips

This API reduces those barriers by recommending destinations based on:

- affordability
- crowd levels
- destination ratings

The system integrates a **tourism dataset of approximately 2000 global destinations** and computes recommendation metrics to identify destinations that minimise common travel barriers.

Users can also create **personal wishlists of destinations** they are interested in visiting.

This project was developed for the **COMP3011 Web Services and Web Data coursework**, which requires students to design and implement a **data-driven API with database integration and CRUD functionality**.

---

# Key Features

- RESTful API built using **FastAPI**
- Integration of a tourism dataset stored in **SQLite**
- Recommendation scoring system including:
  - affordability score
  - quietness score
  - barrier-friendly recommendation score
- **CRUD functionality for wishlists**
- **JWT authentication** for user accounts
- **Pagination support** for large datasets
- **Error handling and validation**
- **Automated testing using pytest**
- Interactive API documentation using **Swagger UI**

---

# Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API framework |
| SQLite | Relational database |
| SQLAlchemy | ORM for database access |
| Pandas | Dataset import and preprocessing |
| JWT | Authentication |
| Pytest | Automated testing |

---

# Design Decisions

## FastAPI

FastAPI was selected because it provides:

- automatic OpenAPI documentation
- strong type validation using Pydantic
- high performance compared to traditional frameworks
- easy integration with SQLAlchemy

These features make it well suited to building modern REST APIs.

## SQLite

SQLite was selected because:

- it is lightweight
- requires no external database server
- works well for development and coursework environments

This allowed the API to remain easy to run locally.

## SQLAlchemy

SQLAlchemy was used as an ORM to:

- simplify database interaction
- support clear data models
- enable maintainable database queries

## Dataset Integration

The tourism dataset was imported using **Pandas** through a dedicated import script. This approach allowed:

- efficient dataset preprocessing
- validation and cleaning of rows
- automated database insertion

---

# System Architecture

The system follows a layered architecture separating API endpoints, business logic, and database access.

Client  
↓  
FastAPI Endpoints  
↓  
Authentication Layer (JWT)  
↓  
Recommendation Engine  
↓  
SQLAlchemy ORM  
↓  
SQLite Database  

This design improves:

- modularity
- maintainability
- testability

---

# Dataset

The API uses a tourism dataset containing approximately **2000 global destinations**.

Each record contains:

- destination name
- country
- continent
- destination type
- estimated travel cost
- visitor rating
- annual visitor numbers
- best season
- UNESCO heritage indicator

The dataset is imported into the database using a **Python import script built with Pandas**.

---

# Database Schema

## Destinations

Stores tourism data.

| Field | Description |
|---|---|
| id | primary key |
| name | destination name |
| country | country |
| continent | continent |
| type | destination type |
| best_season | recommended travel season |
| avg_cost_usd | estimated travel cost |
| rating | visitor rating |
| annual_visitors_m | number of annual visitors |
| unesco | UNESCO heritage indicator |

---

## Users

| Field | Description |
|---|---|
| id | primary key |
| email | user email |
| password_hash | hashed password |

---

## Wishlists

| Field | Description |
|---|---|
| id | primary key |
| name | wishlist name |
| description | wishlist description |
| user_id | associated user |

---

## Wishlist Items

| Field | Description |
|---|---|
| id | primary key |
| wishlist_id | associated wishlist |
| destination_id | saved destination |
| notes | optional notes |

---

# Recommendation Scoring

The recommendation engine evaluates destinations using metrics designed to reduce travel barriers.

## Affordability Score

Measures how inexpensive a destination is relative to others.

## Quietness Score

Measures crowd levels based on annual visitor numbers.

## Quality Score

Based on destination ratings.

## Barrier-Friendly Recommendation Score

A weighted combination of affordability, quietness, and quality metrics used to rank recommended destinations.

---

# API Endpoints

## Destinations

GET /destinations  
Retrieve destinations with pagination.

GET /destinations/{id}  
Retrieve destination by ID.

GET /destinations/count  
Get total number of destinations.

Example request:

GET /destinations?limit=20&offset=0

Example response:

[
  {
    "id": 41,
    "name": "Serene Temple",
    "country": "Morocco",
    "continent": "Africa",
    "avg_cost_usd": 174.84,
    "rating": 4.5
  }
]

---

## Authentication

POST /auth/register  
Register a user.

POST /auth/login  
Authenticate and return JWT token.

---

## Wishlists

POST /wishlists  
Create wishlist.

GET /wishlists  
Retrieve wishlists.

GET /wishlists/{id}  
Retrieve specific wishlist.

POST /wishlists/{id}/items  
Add destination to wishlist.

DELETE /wishlists/{id}/items/{item_id}  
Remove destination.

---

# Installation

Clone the repository:

git clone https://github.com/username/travel-without-barriers-api.git  
cd travel-without-barriers-api

Create a virtual environment:

python -m venv .venv  
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

---

# Import Dataset

Import tourism dataset into the database:

python scripts/import_destinations.py

The script loads the dataset using Pandas, performs cleaning, and inserts records into the destinations table.

---

# Running the API

Start the server:

uvicorn app.main:app --reload

API available at:

http://127.0.0.1:8000

Interactive documentation:

http://127.0.0.1:8000/docs

---

# Testing Strategy

Automated tests are implemented using **pytest**.

Tests include:

- validation of scoring functions
- API endpoint behaviour
- authentication workflow
- wishlist CRUD operations

Tests can be executed using:

pytest -q

Testing ensures the reliability of both the recommendation logic and API endpoints.

---

# Quick Start (Step-by-Step)

Follow these steps to run the API locally.

### 1. Clone the repository

git clone https://github.com/sarahphiri/web_services_coursework.git  
cd web_services_coursework

### 2. Create a virtual environment

python -m venv .venv

Activate the environment:

Mac/Linux

source .venv/bin/activate

Windows

.venv\Scripts\activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Import the dataset

Before running the API, populate the database with the tourism dataset.

python scripts/import_destinations.py

This script will:

- load the dataset using Pandas
- perform basic data cleaning
- create the SQLite database if it does not exist
- insert the destination records into the `destinations` table

### 5. Start the API server

uvicorn app.main:app --reload

The API will start locally at:

http://127.0.0.1:8000

### 6. Open the API documentation

FastAPI automatically generates interactive documentation.

Swagger UI:

http://127.0.0.1:8000/docs

ReDoc:

http://127.0.0.1:8000/redoc

# Using the API

Once the server is running, you can interact with the API using:

- Swagger UI (recommended)
- Postman
- curl
- any HTTP client

### Example workflow

1) Retrieve available destinations

GET /destinations

Example:

GET http://127.0.0.1:8000/destinations?limit=20&offset=0

This returns a paginated list of travel destinations.

---

2) Register a user account

POST /auth/register

Example request body:

{
  "email": "user@example.com",
  "password": "securepassword"
}

---

3) Log in to obtain a JWT token

POST /auth/login

Response:

{
  "access_token": "...",
  "token_type": "bearer"
}

---

4) Create a wishlist

POST /wishlists

Authenticated users can create wishlists to store destinations they are interested in.

---

5) Add destinations to a wishlist

POST /wishlists/{id}/items

This allows users to save recommended destinations for future trips.

---

This workflow demonstrates how the API can be used to discover destinations and organise travel plans.

# Error Handling

The API implements structured error handling to ensure robust behaviour.

Examples include:

- 400 Bad Request for invalid input
- 401 Unauthorized for authentication failures
- 404 Not Found for missing resources
- 409 Conflict for duplicate entries

Validation is implemented using FastAPI and Pydantic models.

---

# Version Control

The project uses **Git and GitHub for version control**.

The repository includes:

- consistent commit history
- modular code organisation
- documented setup instructions
- reproducible project environment

---

# Generative AI Usage

Generative AI tools were used during the development of this project to support:

- architecture planning
- debugging
- generating dataset import scripts
- refining documentation
- exploring alternative implementation approaches

AI assistance was used in a **methodologically structured way**, supporting productivity while ensuring that all design decisions and implementation details were fully understood and verified by the developer.

Conversation logs and usage details are included in the technical report as required by the coursework guidelines.

---

# Future Improvements

Potential future improvements include:

- personalised travel recommendations
- machine learning recommendation models
- integration with external travel APIs
- advanced filtering and search
- deployment to a cloud hosting platform

---

# License

MIT License

EOF

## API Documentation

Full API documentation is available here:

[API Documentation PDF](Travel_Without_Barriers_API_Documentation.pdf)