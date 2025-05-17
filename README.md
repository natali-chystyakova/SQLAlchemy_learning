# SQLAlchemy_learning
The project uses PostgreSQL running in a Docker container and interacts with it via SQLAlchemy ORM.
All migrations are performed using Alembic, and data is validated via Pydantic within a web application on FastAPI.


SQLAlchemy, FastAPI, Pydantic и Alembic, with full insulation through Docker.

🔧 Technologies:

* SQLAlchemy – ORM-layer for describing models and working with PostgreSQL.
* Alembic – Managing database migrations.
* Pydantic – validation and serialization of input/output data.
* Docker – containerization of application and database
* PostgreSQL – the main relational DBMS.
* FastAPI – a core web framework that provides asynchronous endpoints.

The database is launched locally in the PostgreSQL container described in docker-compose.yml.

🚀 Project Startup

🔌 1. Start the Database: make d-run-i-local-dev

🏃 2. Start the Application: python src/main.py

By default, the app will be available at:
👉 http://127.0.0.1:8000/docs

📦 Database Migrations (Alembic)
* Creating a New Migration: make db-revision
* Applying Migrations to the Database: make db-upgrade