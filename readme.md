<h3>chapter 1 Docker</h3>
<ol>
<li>create a virtual(pipenv) environment locally and install Django and strat a django project</li>

<li>write a Dockerfile and then build the initial image</li>
<li>write a docker-compose.yml file and run the container with docker-compose up</li>
</ol>
<h3>chapter 2 Postgres</h3>
<ol>
<li>install a database adapter, psycopg2, so Python can talk to PostgreSQL.</li>
<li>update the DATABASE config in our settings.py file.</li>
<li>add the database service in <b>docker-compose.yml</b></li>
</ol>

### Chapter 3  Custom User Model
* Add custom user model to add custom fields.

### Chapter 4 Pages App
* use of `django.views.generic`'s TemplateView.

### Chapter 5 User Registration
* user login/logout using simple auth app.
* user registration using custom view.

### Chapter 7 Advanced User Registration using allauth
* migrate from auth to allauth
* implement social login

### chapter 8 Environment Variables
* hide all secrets and configurable data in .env(added to .gitignore)

### chapter 9 Customize Emails
* configure smtp.
* customize the default email templates.

### chapter 10 
* create book model
* views to look into books

### chapter 11 file/image uploads
* upload of media book covers

### chapter 12 Reviews app
* post reviews to the book

### chapter 14 orders with stripe
* payments handling

### chapter 15 search
* added search on navbar, q filters with title and author
* improved styling

### adding cart functionality
* cart added
* calculation of total cost, total items in the cart.
