from flask import request, jsonify
from app import app
from .const import HttpStatus
from ..utils.table import tableCaching
from json import dumps as jsonstring

@app.route('/api/v1/tables', methods=['GET'])
async def tables():
  if request.method == 'GET':
      p_type            = request.args.get('type', default=None, type=str)
      p_class_year      = request.args.get('class_year', default=None, type=str)
      p_year            = request.args.get('year', default=None, type=str)
      p_semester        = request.args.get('semester', default=None, type=str)
      p_id              = request.args.get('id', default=None, type=str)
      
      courses = await tableCaching()
      res_courses = []

      for course in courses:
        is_pass = True
        if p_type and course.type != p_type:
          is_pass = False

        if p_class_year and course.class_year != p_class_year:
          is_pass = False

        if p_year and course.year != p_year:
          is_pass = False

        if p_semester and course.semester != p_semester:
          is_pass = False

        if p_id and course.id != p_id:
          is_pass = False

        if is_pass:
          res_courses.append(course.toDict())

      construct = {
          'data': res_courses,
          'success': True,
      }
      response = jsonify(construct)
      response.status_code = HttpStatus.OK
  
  return response
