# Library Service

## Project Description:
This is implement an online management system for book borrowings.

## Requirements:
### Functional:
 * Web-based
 * Manage books inventory
 * Manage books borrowing
 * Manage customers
 * Display notifications
 * Handle payments

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
   - GET:                 books/id/      - get book detail info 
   - PUT/PATCH:    books/id/      - update book (also manage inventory)
   - DELETE:          books/id/      - delete book

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
   - GET:              borrowings/id/  			- get specific borrowing 
   - POST: 	          borrowings/id/return/ 		- set actual return date (inventory should be made += 1)

#### Notifications Service (Telegram):
1. Notifications about new borrowing created, borrowings overdue & successful payment
2. Django Celery uses for sending notifications
3. Other services interact with it to send notifications to library administrators.
4. Usage of Telegram API, Telegram Chats & Bots.

#### Payments Service (Stripe):
1. Perform payments for book borrowings through the platform.
2. Interact with Stripe API using the `stripe` package.
3. API:
   - GET:		success/	- check successful stripe payment
   - GET:		cancel/ 	- return payment paused message


### Technologies to use:
1. Python, SQLite, Git.
2. Django and Django REST framework
3. Telegram Api
4. Django-Celery as task scheduler.
5. JWT authentication with djangoframework-simplejwt
6. Stripe Payments
7. Swagger drf-spectacular.


### How to run:
* Upload project: `git clone https://github.com/zazmarga/library_service`
* Create venv: `python -m venv venv`
* Activate it: `venv/Scripts/activate`
* Create .env file with variables (see env.sample):
     * get BOT_TOKEN & CHAT_ID from Telegram
     * get STRIPE_SECRET_KEY & STRIPE_PUBLISHABLE_KEY
* Run docker image with containers: `docker-compose up --build`
* Go into container `docker exec -it library_service-web-1 sh`
* /code # `python manage.py createsuperuser` (with email & password)
* Go to `admin/`   for create Periodic task
* for register task: `borrowing.tasks.daily_checking_borrowings` create Crontab Schedule (daily)
* get Token: `api/users/token/`
