import re

def find_course_type(id):
  course_type   = ""
  
  if re.match(r"010[\d]{5}", id):
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