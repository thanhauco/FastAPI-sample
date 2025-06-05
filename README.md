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

* User authentication and authorization
* CRUD operations for inventory items
* Category management for items
* File upload support for item images
* Search and filtering capabilities
* Statistics and reporting
* SQLite database
* Automatic API documentation
* Input validation
* Error handling

### API Endpoints

#### Authentication

* `POST /token` \- Login and get access token
* `POST /users/` \- Create new user

#### Categories

* `POST /categories/` \- Create new category
* `GET /categories/` \- List all categories

#### Items

* `POST /items/` \- Create a new item
* `GET /items/` \- List all items \(with search and category filters\)
* `GET /items/{item_id}` \- Get a specific item
* `PUT /items/{item_id}` \- Update an item
* `DELETE /items/{item_id}` \- Delete an item
* `POST /items/{item_id}/upload-image` \- Upload an image for an item

#### Statistics

* `GET /statistics/` \- Get inventory statistics

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Create a user using the `/users/` endpoint
2. Get an access token using the `/token` endpoint
3. Include the token in the Authorization header: `Bearer <token>`

### Search and Filtering

The `/items/` endpoint supports:

* Search by item name
* Filter by category
* Pagination with skip and limit parameters

### Statistics

The `/statistics/` endpoint provides:

* Total number of items
* Total quantity across all items
* Statistics per category (item count and total quantity)