 TrekVista – Trekking Management Application

## Project Overview

TrekVista is a web-based Trekking Management Application developed using Flask, SQLAlchemy, SQLite, Jinja2, HTML, CSS, and Bootstrap. The application provides role-based access for Admin, Trek Staff, and Users to manage trekking activities efficiently.

## Features

### Admin
- Login with predefined credentials
- Dashboard with statistics
- Add, edit, and remove treks
- Assign staff to treks
- Approve and blacklist staff
- Blacklist users
- Search users, staff, and treks
- View all booking records

### Trek Staff
- Register and log in
- Access dashboard after admin approval
- View assigned treks
- Update available slots
- Change trek and booking status
- View trek participants
- Edit profile

### User (Trekker)
- Register and log in
- Browse available treks
- Search by location
- Filter by difficulty
- Book treks
- View booking history
- Edit profile

## Technologies Used

- Flask
- SQLAlchemy
- SQLite
- Jinja2
- HTML5
- CSS3
- Bootstrap 5

## Project Structure
        ```
.
├── application/
│   ├── initial_data.py
│   ├── model.py
│   └── routes.py
│
├── instance/
│
├── static/
│   └── images/
│
├── templates/
│   ├── admin/
│   ├── staff/
│   ├── user/
│   └── home.html
│
├── app.py
├── requirements.txt
├── README.md
└── Finalreport.pdf
```

## Installation

1. Clone the repository

```
git clone <repository-url>
```

2. Create and activate a virtual environment

```
python -m venv venv
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Run the application

```
python app.py
```

5. Open the browser

```
http://127.0.0.1:5000
```

## Database

The SQLite database is created programmatically using SQLAlchemy models.

## Author

Shriya Keshri


