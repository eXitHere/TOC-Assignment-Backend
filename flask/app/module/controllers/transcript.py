from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from pdf2image import convert_from_path, convert_from_bytes 
import cv2
from PIL import Image
import pytesseract
import easyocr
from pytesseract import Output
from matplotlib import pyplot as plt
import numpy as np
import re
from app import app
from ..utils.table import findById
from ..utils.course import find_course_type
from .const import HttpStatus

# allow only .pdf file !
ALLOWED_EXTENSIONS = {'pdf'}

custom_config = r'--oem 1 --psm 6'

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @auth.login_required
@app.route('/api/v1/uploader', methods = ['POST'])
async def upload_file():
  try:
    if request.method == 'POST':
      if 'file' not in request.files:
        return 'No file part'

      f = request.files['file']

      if f.filename == '':
        return "No file selected"
      
      if f and allowed_file(f.filename):
        filename = secure_filename(f.filename)

        pages    = convert_from_bytes(f.read(), 500)
        
        page     = pages[0]
        # preprocess image
        img     = np.array(page)
        img     = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh  = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        invert  = 255 - thresh

        img     = invert
        output  = ""

        # top
        y       = 700
        x       = 0
        h       = 550
        w       = 4134
        crop    = img[y:y+h, x:x+w]
        crop    = cv2.resize(crop, (crop.shape[1]*2, crop.shape[0]*2))
        output += pytesseract.image_to_string(crop,config=custom_config, lang='eng')

        # left
        y       = 1250
        x       = 0
        h       = 4597
        w       = 2067

        crop    = img[y:y+h, x:x+w]
        crop    = cv2.resize(crop, (crop.shape[1]*2, crop.shape[0]*2))
        output += pytesseract.image_to_string(crop,config=custom_config, lang='eng')

        # right
        y       = 1250
        x       = 2067
        h       = 4597
        w       = 2067
        crop    = img[y:y+h, x:x+w]
        crop    = cv2.resize(crop, (crop.shape[1]*2, crop.shape[0]*2))
        output += pytesseract.image_to_string(crop,config=custom_config, lang='eng')

        pdf_string = output

        regex      = {
          "name": r'Name [Mrs]{2,3}.(?P<name>[-\w ]+)\n',
          "birthdayAndStudentId": r'Date of Birth (?P<birthday>[\w, ]+) StudentID (?P<studentId>\d{8})\n',
          "admission": r'Date of Admission\s*(?P<admission_year>\d{4})',
          "degree": r'Degree (?P<degree>[\w ]+)\n',
          "major": r'Major (?P<major>[\w ]+)\n',
          "semester": r'(?s)(?P<semester>\w{3}) Semester, Y\s*ear\s*, (?P<year>\d{4}-\d{4})\n(?P<courseInSem>.*?)GPS\s*: (?P<GPS>[\d.-]+) GPA\s*: (?P<GPA>[\d.-]+)\n',
          "courseInfo": r'(?P<courseID>\d{8}) (?P<courseName>.*?) (?P<credit>\d)\s*(?P<grade>[ABCDF+]*)\n(?P<namekern>[A-Z123 ]*)[\n]*',
          "cumuGPA": r'Cumulative GPA\s*: (?P<cumuGPA>\d.\d{2})',
          "totalCredit": r'Total number of credit earned\s*:\s*(?P<total_credit>\d{1,3})'
        }

        payload              = {}

        minify_string        = re.sub(r'\n{2,}', '\n', pdf_string)
        name                 = re.search(regex['name'], minify_string)
        birthdayAndStudentId = re.search(regex['birthdayAndStudentId'], minify_string)
        admission            = re.search(regex['admission'], minify_string)
        degree               = re.search(regex['degree'], minify_string)
        major                = re.search(regex['major'], minify_string)
        cumuGPA              = re.search(regex['cumuGPA'], minify_string)
        totalCredit          = re.search(regex['totalCredit'], minify_string)
        semesters            = re.findall(regex['semester'], minify_string)

        subjects             = []
        for semester in semesters:

          # fixed OCR Error
          if semester[0] == 'Ist':
            sem = '1st'
          else:
            sem = semester[0]

          semester_data = {
              "semester": sem,
              "year": semester[1],
              "GPS": semester[3],
              "GPA": semester[4],
              "courses": []
          }

          courses_insem = re.findall(regex['courseInfo'], semester[2])

          for course in courses_insem:
              course_data = {
                  "courseId": course[0],
                  "courseName": "",
                  "credit": course[2],
                  "grade": course[3]
              }
              remain     = ""
              if course[4] != "":
                  remain = " " + course[4]

              course_data["courseName"] = course[1] + remain
              semester_data['courses'].append(course_data)
          subjects.append(semester_data)

        payload['studentId']      = birthdayAndStudentId.group('studentId')
        payload['name']           = name.group('name')
        payload['birthday']       = birthdayAndStudentId.group('birthday')
        payload['admission_year'] = admission.group('admission_year')
        payload['degree']         = degree.group('degree')
        payload['major']          = major.group('major')
        payload['total_credit']   = totalCredit.group('total_credit')
        payload['cumuGPA']        = cumuGPA.group('cumuGPA')
        payload['subjects']       = subjects

        subjects = []

        # credit recommends
        credit_recommends = {
          'department': 20,
          'specific_department': 9,
          'language': 12,
          'human': 6,
          'social': 6,
          'free': 6,
          'sciMath': 6
        }

        credit_counter = {
          'department': 0,
          'specific_department': 0,
          'language': 0,
          'human': 0,
          'social': 0,
          'free': 0,
          'sciMath': 0
        }

        course_recommends = [
          ['01006030', '01076001', '01076002', '01006028'],
          ['01006031', '01076003', '01076004', '01076012'],
          ['01006032', '01076005', '01076006', '01076007'],
          ['01076253', '01076008', '01076009', '01076010'],
          ['01076011', '01076263'],
          ['01076013', '01076014'],
          ['01076311', '01076312', '01076015']
        ]

        for idx, subject in enumerate(payload['subjects']):
          courses = []

          # remove current term
          if idx == len(payload['subjects'])-1:
            break

          for idxx, course in enumerate(subject['courses']):
            course_type = find_course_type(course['courseId'])
            curr_course = payload['subjects'][idx]['courses'][idxx]

            courses.append({
                            'course_type': course_type, 
                            'id': curr_course['courseId'], 
                            'name': curr_course['courseName']
                          })

            credit_counter[course_type] += int(curr_course['credit'])

            payload['subjects'][idx]['courses'][idxx] = {
                                                          'course_type': course_type, 
                                                          'id': curr_course['courseId'], 
                                                          'name': curr_course['courseName']
                                                        }
          subjects.append(courses)
          
        _course_recommends = []

        for _id in course_recommends[len(payload['subjects'])-1]:
          _courses = await findById(_id)
          for __course in _courses:
            _course_recommends.append(__course.to_dict())
        
        construct = {
          'data': {
                'credit_recommends': credit_recommends, 
                'credit_counter': credit_counter, 
                'course_recommends': _course_recommends, 
                'name': payload['name'], 
                'student_id': payload['studentId'], 
                'subjects': subjects
            },
          'success': True,
        }

        response = jsonify(construct)
        response.status_code = HttpStatus.OK

        

  except Exception as e: 
    print(e)

    response = jsonify({
      'error': 'unknown error!'
    })

    response.status_code = HttpStatus.BAD_REQUEST

  return response


"""
- กลุ่มวิชาวิทยาศาสตร์กับคณิตศาสตร์ 6 หน่วยกิต
- กลุ่มวิชาภาษา 12 หน่วยกิต
- กลุ่มวิชามนุษยศาสตร์ 6 หน่วยกิต
- กลุ่มวิชาสังคมศาสตร์ 6 หน่วยกิต
"""