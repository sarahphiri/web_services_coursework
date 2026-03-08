# Travel Without Barriers

Travel Without Barriers is a full-stack travel recommendation platform designed to help people who face financial or mental health barriers to travel discover destinations that are easier and less stressful to plan.

The system recommends destinations based on:

- affordability
- crowd levels
- destination ratings
- overall accessibility

Users can also create personal wishlists of destinations they want to visit.

This project was developed for the **COMP3011 Web Services and Web Data coursework** at the **University of Leeds**.

---

# Live Deployment

Frontend (Web Application)  
https://web-services-coursework.vercel.app

Backend API  
https://webservicescoursework-production.up.railway.app

Interactive API Documentation  
https://webservicescoursework-production.up.railway.app/docs

---

# GitHub Repository

https://github.com/sarahphiri/web_services_coursework

---

# Project Overview

Many people want to travel but feel overwhelmed by:

- high travel costs
- overcrowded tourist destinations
- complex travel planning
- uncertainty about where to start

Travel Without Barriers reduces these obstacles by recommending destinations that are:

- cheaper
- less crowded
- highly rated
- easier to plan

The backend API processes tourism data and computes recommendation metrics that help users discover accessible travel options.

---

# Key Features

## Destination Recommendation System

Destinations are ranked using calculated metrics including:

- Affordability Score
- Quietness Score
- Quality Score
- Hidden Gem Score
- Barrier Score

These metrics help identify destinations that minimise common travel barriers.

---

## User Authentication

Users can create accounts and log in securely.

Authentication allows users to:

- create wishlists
- save destinations
- manage their travel plans

---

## Wishlist Management

The system supports full CRUD operations for wishlists.

Users can:

- create wishlists
- add destinations to a wishlist
- remove destinations
- delete wishlists

---

## Destination Filtering

Destinations can be filtered by:

- continent
- country
- affordability score
- quietness score
- hidden gem score

This allows users to explore destinations that match their preferences.

---

# Technology Stack

## Backend

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Uvicorn

FastAPI was chosen because it provides:

- automatic API documentation
- request validation using Pydantic
- high performance
- clean REST API design

---

## Frontend

- Next.js
- React
- Tailwind CSS

Next.js enables rapid UI development and integrates easily with Vercel deployment.

---

## Deployment

- Frontend: Vercel
- Backend: Railway

---

# Dataset

Dataset Source:  
https://www.kaggle.com/datasets/cosmox23/popular-tourist-destinations-and-their-features

The dataset contains approximately **2000 global tourist destinations** and includes:

- destination name
- country
- continent
- destination type
- estimated cost
- visitor rating
- annual visitor numbers
- best season to visit

These attributes allow the API to compute recommendation metrics.

---

# Recommendation Metrics

## Affordability Score

Lower travel costs produce higher scores.

```
Affordability Score = 1000 / (avg_cost_usd + 1)
```

---

## Quietness Score

Destinations with fewer visitors receive higher scores.

```
Quietness Score = 10 / (annual_visitors_m + 1)
```

---

## Quality Score

Represents the destination rating directly.

```
Quality Score = rating
```

---

## Hidden Gem Score

Combines high quality with low visitor numbers.

```
Hidden Gem Score = rating + Quietness Score
```

---

## Barrier Score (Overall Recommendation)

Combines affordability, quietness, and quality.

```
Barrier Score = Affordability Score + Quietness Score + Quality Score
```

Destinations with the highest barrier scores are recommended first.

---

# Database Schema

## Destinations

Stores imported tourism dataset.

Fields include:

- id
- name
- country
- continent
- type
- best_season
- avg_cost_usd
- rating
- annual_visitors_m
- unesco

---

## Users

Stores registered users.

Fields include:

- id
- email
- password

---

## Wishlists

Stores user-created wishlists.

Fields include:

- id
- user_id
- name
- description
- created_at

---

## Wishlist Items

Stores destinations saved to wishlists.

Fields include:

- id
- wishlist_id
- destination_id
- notes
- priority
- created_at

---

# Local Setup Guide

These instructions allow the project to be run locally.

---

## 1 Clone the repository

```bash
git clone https://github.com/sarahphiri/web_services_coursework.git
cd web_services_coursework
```

---

## 2 Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment.

Mac / Linux

```bash
source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

---

## 3 Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4 Import the dataset

Navigate to the scripts directory.

```bash
cd scripts
```

Run the import script.

```bash
python import_destinations.py
```

This will populate the SQLite database (`travel.db`) with the tourism dataset.

---

## 5 Start the FastAPI backend

From the project root run:

```bash
uvicorn app.main:app --reload
```

The API will run at:

```
http://127.0.0.1:8000
```

API documentation:

```
http://127.0.0.1:8000/docs
```

---

## 6 Run the frontend

Navigate to the frontend directory.

```bash
cd travel-without-barriers-frontend
```

Install dependencies.

```bash
npm install
```

Start the development server.

```bash
npm run dev
```

The frontend will run at:

```
http://localhost:3000
```

---

# Testing the API

The easiest way to test the API is using the built-in FastAPI documentation.

Open:

```
http://127.0.0.1:8000/docs
```

This interface allows interactive testing of all endpoints.

---

## Using the Deployed Application

The easiest way to use the system is through the live deployment.

### Web Application

Open the deployed frontend:

https://web-services-coursework.vercel.app

From the website you can:

- browse recommended travel destinations
- filter destinations by accessibility metrics
- register a user account
- log in to the system
- create and manage wishlists
- add destinations to wishlists

The frontend communicates with the deployed backend API hosted on Railway.

### Backend API

The backend REST API is available at:

https://webservicescoursework-production.up.railway.app

Interactive API documentation is available through FastAPI Swagger:

https://webservicescoursework-production.up.railway.app/docs

The documentation interface allows endpoints to be tested directly in the browser.

### Example API Request

You can retrieve destination recommendations by opening:

https://webservicescoursework-production.up.railway.app/recommendations

This will return recommended destinations in JSON format.

### Testing Authentication

User accounts can be created through the frontend interface, or by using the API documentation.

For example, in the Swagger interface:

1. open `/docs`
2. select `POST /auth/register`
3. provide an email and password
4. execute the request

Once registered, users can log in and manage wishlists through the frontend interface.

---

# Model Context Protocol (MCP) Integration

The project also includes a Model Context Protocol (MCP) server which allows AI systems to interact with the Travel Without Barriers API.

MCP enables large language models and other AI clients to call structured tools that interact with real services. In this project, the MCP server exposes selected backend functionality as AI-accessible tools.

Importantly, the MCP server does not maintain a separate local database as its source of truth. Instead, it sends HTTP requests to the deployed FastAPI backend. This means MCP interactions affect the same live system used by the frontend web application.

This ensures that:

- MCP interactions affect the live deployed database  
- the frontend and AI interfaces share the same backend  
- wishlists created via MCP appear in the web application  
- recommendations retrieved via MCP use the same scoring logic as the website  

## MCP Architecture

The MCP server works as a thin wrapper around the deployed API.

The process works as follows:

1. An AI client sends a tool request to the MCP server.  
2. The MCP server translates the request into an HTTP request.  
3. The request is sent to the deployed FastAPI backend.  
4. The backend returns a response.  
5. The MCP server returns that response to the AI system.

Because the MCP server calls the deployed API rather than a local database, the backend remains the single source of truth for the system.

## MCP Tools

The MCP server exposes several tools that mirror the backend API functionality.

Examples include:

- retrieve destination recommendations  
- register users  
- login users  
- list wishlists  
- create wishlists  
- delete wishlists  

Each MCP tool internally calls the corresponding REST API endpoint.

## Running the MCP Server Locally

To start the MCP server locally:

    python mcp_server.py

This starts the MCP service so that an MCP client can connect to it.

## Testing the MCP Server

The MCP server can be tested using the MCP Inspector.

### Step 1 — Navigate to the project directory

    cd web_services_coursework

### Step 2 — Start the MCP Inspector

Run the following command:

    npx -y @modelcontextprotocol/inspector python mcp_server.py

This launches the MCP Inspector and opens a local interface in your browser.

### Step 3 — View available MCP tools

Inside the Inspector, open the **Tools** panel.

You should see tools such as:

- get_recommendations  
- register_user  
- login_user  
- list_wishlists  
- create_wishlist  
- delete_wishlist  

### Step 4 — Test the recommendation system

Run the recommendation tool using example parameters such as:

- continent: Europe  
- sort_by: affordability  

The MCP server will return recommendations from the deployed API.

### Step 5 — Test wishlist creation

Use the create_wishlist tool with valid user credentials.

Example inputs:

- email: your registered email  
- password: your password  
- name: MCP Test Wishlist  
- description: Created via MCP  

### Step 6 — Verify the frontend updates

After creating a wishlist via MCP:

1. open the deployed frontend application  
2. log in using the same account  
3. navigate to the wishlists page  

If the wishlist appears on the website, this confirms that the MCP server is correctly interacting with the deployed backend.

## Why MCP Was Included

MCP was implemented to demonstrate a creative application of generative AI within the project.

It allows AI systems to:

- query the recommendation system  
- create and manage wishlists  
- interact with the travel planning service programmatically  

This extends the project beyond a traditional REST API by enabling AI-driven interaction with the deployed system.

---

# Generative AI Usage

Generative AI tools were used during development to assist with:

- dataset discovery
- recommendation metric design
- database schema ideas
- debugging implementation issues
- documentation generation
- prompt engineering
- branding design

Tools used:

- ChatGPT
- Gemini (for logo and design guidance)

All generated code and suggestions were reviewed and adapted before integration.

---

# Licence

Dataset released under the MIT License.

Copyright (c) 2013 Mark Otto  
Copyright (c) 2017 Andrew Fong  

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files to deal in the Software without restriction.

The software is provided **"as is"**, without warranty of any kind.

---

---

# API Documentation

Full API documentation for the Travel Without Barriers backend can be found here:

https://github.com/sarahphiri/web_services_coursework/blob/main/TWB_API_Documentation.pdf

This document contains:

- detailed descriptions of all API endpoints
- authentication process and token usage
- request parameters and example requests
- example API responses
- error handling and status codes
- system architecture explanation

The documentation provides a complete reference for developers who wish to interact with the API directly.

---

# Author

Sarah Phiri  
BSc Computer Science  
University of Leeds