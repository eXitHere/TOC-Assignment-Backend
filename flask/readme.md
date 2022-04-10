## installation

```
# create env
$ python3 -m venv env
```

```
# macOS/Linux
$ source ./env/bin/active
```

```
# Windows
$ env/Scripts/active
```

```
# install dependencies
$ pip install -r requirements.txt
```

## developer

```
python run.js
```

```
route
- '/'
- '/api/v1/tables'
  # example
  + /api/v1/tables?sorted_by=name&course_type=free
  + /api/v1/tables?sorted_by=name&teacher=สย
  # Params
  + sorted_by=string
  + class_year=stringส
  + year=string
  + semester=string
  + id=string
  + teacher=string <regex>
- /api/v1/uploader
  # type: form-data

  # body:
  + file: doc.pdf
```

```
docker build -t toc-flask-container .
docker run -p 8000:8000 toc-flask-container
``