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

## Contributing

Since this is a repository for a tutorial, the code should remain the same as the code that was shown in the tutorial. Any pull requests that don't address security flaws or fixes for language updates will be automatically closed. Style changes, adding libraries, etc are not valid changes for submitting a pull request.
