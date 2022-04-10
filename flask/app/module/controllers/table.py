from flask import request, jsonify
from app import app
from .const import HttpStatus
from ..utils.table import tableCaching
from json import dumps as jsonstring
import re

@app.route('/api/v1/tables', methods=['GET'])
# @auth.login_required
async def tables():
  if request.method == 'GET':
      p_type            = request.args.get('type', default=None, type=str)
      p_class_year      = request.args.get('class_year', default=None, type=str)
      p_year            = request.args.get('year', default=None, type=str)
      p_semester        = request.args.get('semester', default=None, type=str)
      p_id              = request.args.get('id', default=None, type=str)
      p_teacher         = request.args.get('teacher', default=None, type=str)
      p_sorted_by       = request.args.get('sorted_by', default=None, type=str)
      
      courses = await tableCaching()
      res_courses = []

      if p_sorted_by:
        try:
          courses = sorted(courses, key=lambda x: getattr(x, p_sorted_by), reverse=False)
        except:
          pass

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

        # print(p_teacher)
        # 'teacher': ['ดร.งามเฉิด ด่านพัฒนามงคล']
        if p_teacher:
          found_teacher = False
          for teacher in course.teacher:
            # if p_teacher == teacher:
            if re.search(r"{}".format(p_teacher), teacher):
              found_teacher = True
              break
          if not found_teacher:
            is_pass = False

        if is_pass:
          res_courses.append(course.to_dict())

      construct = {
          'data': res_courses,
          'success': True,
      }

      response = jsonify(construct)
      response.status_code = HttpStatus.OK
  
  return response
