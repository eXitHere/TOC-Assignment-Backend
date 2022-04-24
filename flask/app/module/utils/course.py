import re

def find_course_type(id):
  course_type   = ""
  
  # 010 0 6xxx => department 
  # 010 7 6xxx => specific department
  
  if re.match(r"01076(4[0-9]{2}|5[0-9][0-9])", id):
    course_type = 'specific_department'
  elif re.match(r"0100[\d]{4}", id):
    course_type = 'department'
  elif re.match(r"902[\d]{5}", id):
    course_type = 'language'
  elif re.match(r"903[\d]{5}", id):
    course_type = 'human'
  elif re.match(r"904[\d]{5}", id):
    course_type = 'social'
  elif re.match(r"901[\d]{5}", id):
    course_type = 'sciMath'
  else:
    course_type = 'free'

  return course_type