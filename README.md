# FastAPI Inventory System

A simple inventory management system built with FastAPI, SQLAlchemy, and SQLite.

## English

### Setup

1. Create a virtual environment:

``` bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

``` bash
pip install -r requirements.txt
```

3. Run the application:

``` bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000
API documentation will be available at http://localhost:8000/docs

### Features

* CRUD operations for inventory items
* File upload support for item images
* SQLite database
* Automatic API documentation
* Input validation
* Error handling

### API Endpoints

* `POST /items/` \- Create a new item
* `GET /items/` \- List all items
* `GET /items/{item_id}` \- Get a specific item
* `PUT /items/{item_id}` \- Update an item
* `DELETE /items/{item_id}` \- Delete an item
* `POST /items/{item_id}/upload-image` \- Upload an image for an item