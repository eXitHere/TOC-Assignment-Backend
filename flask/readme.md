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
- '/api/v1/test'
```

```
docker build -t toc-flask-container .
docker run -p 8000:8000 toc-flask-container
```