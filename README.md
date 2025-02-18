# Library Service

## Project Description:
In your city, there’s a library where you can borrow books 
and pay for your borrowings using cash, 
depending on how many days it takes you to read the book.

This is implement an online management system for book borrowings. 
The system will optimize the library administrators’ work 
and make the service much more user-friendly.

## Requirements:
### Functional (what the system should do):
 * Web-based
 * Manage books inventory
 * Manage books borrowing
 * Manage customers
 * Display notifications
 * Handle payments
### Non-functional (what the system should deal with):
 * 5 concurrent users
 * Up to 1000 books
 * 50k borrowings/year
 * ~30MB/year

### Architecture
![here](architecture.png)

### Resources:
#### Book:
 - Title: str
 - Author: str
 - Cover: Enum: HARD | SOFT
 - Inventory*: positive int
 - Daily fee: decimal (in $USD)

 * (*) Inventory – the number of this specific book available now in the library

#### User (Customer):
 - Email: str
 - First name: str
 - Last name: str
 - Password: str
 - Is staff: bool

#### Borrowing:
 - Borrow date: date
 - Expected return date: date
 - Actual return date: date
 - Book id: int
 - User id: int

#### Payment:
 - Status: Enum: PENDING | PAID
 - Type: Enum: PAYMENT | FINE
 - Borrowing id: int
 - Session url: Url  # url to stripe payment session
 - Session id: str  # id of stripe payment session
 - Money to pay: decimal (in $USD)  # calculated borrowing total price

### Components:

#### Books Service:
1. Managing the quantity of books (CRUD for Books)
2. API:
   - POST:               books/             - add new 
   - GET:                 books/              - get a list of books
   - GET:                 books/<id>/      - get book detail info 
   - PUT/PATCH:    books/<id>/      - update book (also manage inventory)
   - DELETE:          books/<id>/      - delete book

#### Users Service:
1. Managing authentication & user registration
2. API:
   - POST:           users/                           - register a new user 
   - POST:           users/token/                 - get JWT tokens 
   - POST:           users/token/refresh/    - refresh JWT token 
   - GET:              users/me/                    - get my profile info 
   - PUT/PATCH: users/me/                    - update profile info 

#### Borrowings Service:
1. Managing users' borrowings of books
2. API:
   - POST:            borrowings/   		                        - add new borrowing (when borrow book - inventory should be made -= 1) 
   - GET:              borrowings/?user_id=...&is_active=...  - get borrowings by user id and whether is borrowing still active or not.
   - GET:              borrowings/<id>/  			- get specific borrowing 
   - POST: 	          borrowings/<id>/return/ 		- set actual return date (inventory should be made += 1)

#### Notifications Service (Telegram):
1. Notifications about new borrowing created, borrowings overdue & successful payment
2. In parallel cluster/process (Django Q package or Django Celery will be used)
3. Other services interact with it to send notifications to library administrators.
4. Usage of Telegram API, Telegram Chats & Bots.

#### Payments Service (Stripe):
1. Perform payments for book borrowings through the platform.
2. Interact with Stripe API using the `stripe` package.
3. API:
   - GET:		success/	- check successful stripe payment
   - GET:		cancel/ 	- return payment paused message
