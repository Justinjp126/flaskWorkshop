# 348 Final Project


## How To Run

1. Install `flask-sqlalchemy & virtualenv`:

```
$ pip install virtualenv
```

2. Then run the command:

```
$ .\\env\Scripts\activate.bat
```

3. Start the web server:

```
$ python app.py
```

## Indexes

student_id
professor_id

Filtering by Student/Professor ID:
Index quickly locate rows with the specified student_id/professor_id. Without this index, the database would have to scan all rows in the assignment table, which could be slow for large datasets.

Joining with Student or Professor:
Database can use the index to find the matching rows in the assignment table without scanning the entire table.

from project import app, db
app.app_context().push()
db.create_all()

## Concurrency

SERIALIZABLE - Locks sets of objects (tables, pages, index ranges)
No phantom data; Most accurate, but slowest (least concurrency); Same as 2PL

## Lessons

Overall, this project taught me the basics of Flask and mySQLAlchemy. I can
now make a CRUD project using these technologies. If I had the chance to
start this project again, I would ensure I designed my project with the
requirements in mind first. I had to go back and change my ORM to prepared
statements, which was an overall unnecessary time drain. I would also try to
spend more time learning the basics of Flask first before starting, to avoid
spending time on what ended up basic issues that I spent a lot of time
debugging.
