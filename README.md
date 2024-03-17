# FlaskIntroduction

This repo has been updated to work with `Python v3.8` and up.

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


from project import app, db
app.app_context().push()
db.create_all()
