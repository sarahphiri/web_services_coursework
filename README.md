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
https://travel-without-barriers.vercel.app

Backend API  
https://travel-without-barriers-production.up.railway.app

Interactive API Documentation  
https://travel-without-barriers-production.up.railway.app/docs

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