# PS1-Fastapi-tasks

Task Manager API
Overview

Task Manager API is a clean, secure REST API for managing projects and tasks.
It includes JWT-based authentication, role-based operations, and centralized error handling.
This project is suitable for hackathons, demos, or as a starter template for production systems.

Tech Stack

FastAPI – API framework

SQLAlchemy – ORM for database models

PostgreSQL / SQLite – Database

JWT – Authentication

Uvicorn – ASGI server

Features

JWT Authentication – Secure login & access control

CRUD Operations – For projects & tasks

Centralized Error Handling – Example: ValueError handler

Auto DB Table Creation – Base.metadata.create_all(bind=engine) on startup

Modular Router Structure – Easy to extend

How to Test

Use Postman / Insomnia to test endpoints

Register a user → Login → Use JWT token in Authorization: Bearer <token>

Perform CRUD operations on /projects/ and /tasks/
