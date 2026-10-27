Little Lemon - Back-end Developer Capstone (Django REST Framework + MySQL)

=====================================================================
API PATHS TO TEST (base URL: http://127.0.0.1:8000)
=====================================================================
/                        Static HTML home page (GET)
/api/registration/       Register a new user (POST: username, email, password)
/api/token/login/        Get an auth token (POST: username, password)
/api/menu/               List menu items (GET, public) / add item (POST, token needed)
/api/menu/<id>/          Single item (GET public; PUT, PATCH, DELETE token needed)
/api/bookings/           List bookings (GET) / create booking (POST) - token needed
/api/bookings/<id>/      Single booking (GET, PUT, PATCH, DELETE) - token needed
/admin/                  Django admin

Authenticated requests need this header:
    Authorization: Token <your-token>

Sample bodies (JSON):
  POST /api/registration/   {"username":"chef","email":"chef@example.com","password":"Str0ng-Passw0rd!"}
  POST /api/token/login/    {"username":"chef","password":"Str0ng-Passw0rd!"}
  POST /api/menu/           {"title":"Greek Salad","price":"12.50","inventory":20}
  POST /api/bookings/       {"name":"Maria","no_of_guests":3,"booking_date":"2026-12-24T19:30:00Z"}

=====================================================================
SETUP
=====================================================================
1. Create the MySQL database:
       mysql -u root -p -e "CREATE DATABASE littlelemon CHARACTER SET utf8mb4;"

2. Create a virtual environment and install dependencies:
       python -m venv venv
       source venv/bin/activate        (Windows: venv\Scripts\activate)
       pip install -r requirements.txt
   (If mysqlclient fails to install, see https://pypi.org/project/mysqlclient/ for OS prerequisites.)

3. Set DB credentials (defaults: user root, host 127.0.0.1, port 3306, db littlelemon):
       export DB_PASSWORD=your_mysql_password       (Windows: set DB_PASSWORD=...)
   Optional: DB_NAME, DB_USER, DB_HOST, DB_PORT

4. Migrate and run:
       python manage.py migrate
       python manage.py createsuperuser     (optional)
       python manage.py runserver

5. Run unit tests (needs a MySQL user allowed to create a test_ database):
       python manage.py test

Quick no-MySQL smoke test only: set USE_SQLITE=1 before the commands above.
