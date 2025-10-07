# Flask Inventory Management (Simple)

A minimal Flask app to manage Products, Locations, and Product Movements with a Balance report.

## Features
- Add/Edit/Delete Products
- Add/Edit/Delete Locations
- Add/Edit/Delete Product Movements (supports incoming/outgoing)
- Balance report per Product per Location

## Tech
- Flask + SQLite (via Flask-SQLAlchemy)
- Bootstrap for UI

## Setup
`ash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
`

App runs at http://127.0.0.1:5000/.

### Seed Sample Data
Open http://127.0.0.1:5000/seed once, then browse the app.

## Screenshots
Add your screenshots here:
- Products page
- Locations page
- Movements page
- Balance report
