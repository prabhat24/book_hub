### 1 Docker
* created a virtual(pipenv) environment.
* Dockerfile
* docker-compose.yml file.

### 2 Postgres
* installed  a database adapter, psycopg2
* updated the DATABASE config in our settings.py file
* added  the database service in <b>docker-compose.yml</b>

### 3  Custom User Model
* Add custom user model to add custom fields.

### 4 Pages App
* use of `django.views.generic`'s TemplateView.

### 5 User Registration
* user login/logout using simple auth app.
* user registration using custom view.

### 7 Advanced User Registration using allauth
* migrate from auth to allauth
* implemented social login

### 8 Environment Variables
* hide all secrets and configurable data in .env(added to .gitignore)

### 9 Customize Emails
* configure smtp.
* customized the default email templates.

### 10 Books App
* created book model
* views to look into books (book_detail & book_list)

### 11 file/image uploads
* uploaded of media book covers

### 12 Reviews app
* post reviews to the book

### 14 orders with stripe
* payments handling

### 15 search
* added search on navbar, q filters with title and author
* improved styling

### 16 adding cart functionality
* cart added
* calculation of total cost, total items in the cart.
* remove from cart

### 17 security
* added ALLOWED HOSTS.
* SQL injection (checked)
* XSS (Cross Site Scripting) (checked)
* checked CSRF (added csrf token on every post calls)
* Clickjacking Protection
* Admin Hardening