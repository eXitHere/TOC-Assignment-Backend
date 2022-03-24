from flask import request, jsonify
from app import app
from .const import HttpStatus

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
      print("<Request: {}>".format(request.json))
  return "<h1>Hello World From Flask</h1>"

@app.route('/api/v1/test', methods=['GET', 'POST'])
def test():
  if request.method == 'GET':
      construct = {
          'error': [],
          'success': True,
      }
      response = jsonify(construct)
      response.status_code = HttpStatus.OK

  elif request.method == 'POST':
      nim = None if request.json['body']['nim'] is "" else request.json['body']['nim']
      name = None if request.json['body']['name'] is "" else request.json['body']['name']
      construct = {}
      try:
          construct['success'] = True
          construct['message'] = 'Data saved'
          response = jsonify(construct)
          response.status_code = HttpStatus.CREATED
      except Exception as e:
          construct['success'] = False
          construct['error'] = str(e)
          response = jsonify(construct)
          response.status_code = HttpStatus.BAD_REQUEST
  return response
