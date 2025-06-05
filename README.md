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
* `POST /token` - Login and get access token
* `POST /users/` - Create new user

#### Categories
* `POST /categories/` - Create new category
* `GET /categories/` - List all categories

#### Items
* `POST /items/` - Create a new item
* `GET /items/` - List all items (with search and category filters)
* `GET /items/{item_id}` - Get a specific item
* `PUT /items/{item_id}` - Update an item
* `DELETE /items/{item_id}` - Delete an item
* `POST /items/{item_id}/upload-image` - Upload an image for an item

#### Statistics
* `GET /statistics/` - Get inventory statistics

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

## Tiếng Việt

### Cài đặt

1. Tạo môi trường ảo:

``` bash
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
```

2. Cài đặt các thư viện cần thiết:

``` bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:

``` bash
uvicorn main:app --reload
```

API sẽ có sẵn tại http://localhost:8000
Tài liệu API sẽ có sẵn tại http://localhost:8000/docs

### Tính năng

* Xác thực và phân quyền người dùng
* Các thao tác CRUD cho các mục trong kho
* Quản lý danh mục cho các mục
* Hỗ trợ tải lên hình ảnh cho các mục
* Tìm kiếm và lọc
* Thống kê và báo cáo
* Cơ sở dữ liệu SQLite
* Tài liệu API tự động
* Kiểm tra đầu vào
* Xử lý lỗi

### Các Endpoint API

#### Xác thực
* `POST /token` - Đăng nhập và lấy token
* `POST /users/` - Tạo người dùng mới

#### Danh mục
* `POST /categories/` - Tạo danh mục mới
* `GET /categories/` - Liệt kê tất cả danh mục

#### Mục hàng
* `POST /items/` - Tạo mục mới
* `GET /items/` - Liệt kê tất cả các mục (với tìm kiếm và lọc theo danh mục)
* `GET /items/{item_id}` - Lấy thông tin một mục cụ thể
* `PUT /items/{item_id}` - Cập nhật một mục
* `DELETE /items/{item_id}` - Xóa một mục
* `POST /items/{item_id}/upload-image` - Tải lên hình ảnh cho một mục

#### Thống kê
* `GET /statistics/` - Lấy thống kê kho

### Xác thực

API sử dụng JWT (JSON Web Tokens) để xác thực. Để truy cập các endpoint được bảo vệ:

1. Tạo người dùng bằng endpoint `/users/`
2. Lấy token bằng endpoint `/token`
3. Thêm token vào header Authorization: `Bearer <token>`

### Tìm kiếm và Lọc

Endpoint `/items/` hỗ trợ:
* Tìm kiếm theo tên mục
* Lọc theo danh mục
* Phân trang với các tham số skip và limit

### Thống kê

Endpoint `/statistics/` cung cấp:
* Tổng số mục
* Tổng số lượng tất cả các mục
* Thống kê theo danh mục (số lượng mục và tổng số lượng)