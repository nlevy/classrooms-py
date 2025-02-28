# Classroom Assignment Service

A service that optimally assigns students to classrooms based on various factors including friendships, gender balance, academic performance, and behavioral considerations.

## Features
- Assigns students to classes while considering:
  - Friend preferences
  - Gender balance
  - Academic performance distribution
  - Behavioral performance distribution
  - "Not with" restrictions
  - Cluster groupings
- REST API endpoints for:
  - Classroom assignment
  - Template data structure
- CLI tool for testing and analysis

## Running the Service

### Development
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   .venv\Scripts\activate     # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   python src/main.py
   ```
   The service will be available at http://localhost:5000

### Production
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run with Gunicorn:
   ```bash
   gunicorn -c gunicorn_config.py src.wsgi:app
   ```
   The service will be available at http://0.0.0.0:8000

Note: For production deployment, ensure proper security measures and environment configurations are in place.

