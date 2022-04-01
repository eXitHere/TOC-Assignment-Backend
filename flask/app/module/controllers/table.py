from flask import request, jsonify
from app import app
from .const import HttpStatus
from ..utils.table import tableCaching

@app.route('/api/v1/tables', methods=['GET'])
async def test():
  if request.method == 'GET':
      data = await tableCaching()
      construct = {
          'data': data,
          'success': True,
      }
      response = jsonify(construct)
      response.status_code = HttpStatus.OK
  
  return response
