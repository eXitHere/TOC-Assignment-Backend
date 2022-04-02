import re

def findCourseType(id):
  course_type = ""
  
  if re.match(r"010[\d]{5}", id):
    course_type = 'ภาค'
  elif re.match(r"902[\d]{5}", id):
    course_type = 'ภาษา'
  elif re.match(r"903[\d]{5}", id):
    course_type = 'มนุษย์'
  elif re.match(r"904[\d]{5}", id):
    course_type = 'สังคม'
  elif re.match(r"901[\d]{5}", id):
    course_type = 'วิทย์'
  else:
    course_type = 'เสรี'

  return course_type