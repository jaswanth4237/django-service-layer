# Django Service Layer vs Signals Benchmark

This project demonstrates  transition from using Django's implicit signal framework for business logic to an explicit, transactionally safe, and highly performant Service Layer architecture.

## Overview

In traditional Django development, `post_save` signals are often used to trigger side-effects like updating aggregated statistics when a model is created. While signals help decouple code, they bring several architectural traps in production:
1. **Bulk Operations Bypass**: Signals do not fire on mass updates like `.update()` or `.bulk_create()`, leading to inconsistent data tracking.
2. **N+1 Performance Overhead**: Firing individual signals iteratively inside a loop triggers expensive, sequential database queries rather than batching them.
3. **Traceability & Test Isolation**: Debugging invisible triggers is heavily error-prone, requiring developers to aggressively mock receivers to maintain standard unit test isolation.

By adopting a strict **Service Layer** paired with `transaction.atomic()`, we guarantee explicit execution boundaries while utilizing robust performance optimizations via database `F()` expressions.

## Core Features

- Containerized architecture via Docker & Docker Compose setup, waiting for a PostgreSQL healthy state automatically.
- Demonstrates Django `post_save` trap when compared to SQL-level `.bulk_create()`.
- Validated test suite showcasing proper signal isolation methodologies (`tearDown` disconnection).
- Implementation of a strict Service Layer resolving signal issues (`orders/services.py`).
- Built-in benchmarking CLI command mathematically proving the 300x+ performance speedup of structured bulk inserts compared to iterative database interactions.

## Local Setup (`Docker`)

1. **Clone the repository.**
2. **Environment File setup:**
   Create an active `.env` file based on the default variables provided:
   ```bash
   cp .env.example .env
   ```
3. **Run Services:**
   Execute Docker Compose to bring the database and application up. Port `8000` will be exposed.
   ```bash
   docker compose up --build -d
   ```

## Running the Verification Test Suite

Tests demonstrate bulk behavior execution bypassing signals compared to successful service-layer integration.
```bash
docker compose exec app python manage.py test
```

## Running the Benchmark Protocol

A custom underlying management command calculates the real-time speed differences between processing batch orders iteratively vs utilizing bulk inserts.
```bash
docker compose exec app python manage.py benchmark_updates
```
*Expected Output Format:* 
```text
Signal approach time: 14.01s
Optimized service time: 0.04s
Speedup factor: 364.47x
```
