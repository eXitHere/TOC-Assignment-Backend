# -*- coding: utf-8 -*-

import time
from pyppeteer import launch
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from app import app
import re
import hashlib
from os.path import exists
from ..model.course import Course
from .course import find_course_type
import json


timestamp     = 0
cacheing_time = 300 # minutes
start_date    = datetime(year=2022, month=1, day=10).replace(microsecond=0,second=0,minute=0, hour=0)
week_count    = 20
data          = {}
daysThai      = ['อาทิตย์', 'จันทร์', 'อังคาร', 'พุธ', 'พฤหัส', 'ศุกร์', 'เสาร์']
daysThai2     = ['อา.', 'จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.']
monthThai     = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']

def minuteToMilSecond(min):
  return min * 60

def date_new_format(old_date):
  data_array = old_date.split()

  if(len(data_array) > 1):
    # ['จันทร์', '23', 'พ.ค.', '2022', '13:30', '-', '16:30']
    d                = daysThai.index(data_array[0])
    m                = monthThai.index(data_array[2])

    # ["13", "30"]
    time_start = data_array[4].split(":")
    time_end   = data_array[6].split(":")

    date_start = datetime(
                          year=int(data_array[3]), 
                          month=int(m), 
                          day=int(data_array[1])
                        )
    date_start = date_start.replace(
                          minute=int(time_start[1]), 
                          hour=int(time_start[0])
                        )

    date_stop   = datetime(
                          year=int(data_array[3]), 
                          month=int(m), 
                          day=int(data_array[1])
                        )
    date_stop   = date_stop.replace(
                          minute=int(time_end[1]), 
                          hour=int(time_end[0])
                        )
    new_format  = {
                  'start': int(date_start.timestamp()), 
                  'end': int(date_stop.timestamp())
                }
  else:
    new_format            = old_date
  
  return new_format

async def fetchNewHTML():

  page_paths = [
    # 'https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_class&selected_year=2564&selected_semester=2&selected_faculty=01&selected_department=05&selected_curriculum=06&selected_class_year=3&search_all_faculty=false&search_all_department=false&search_all_curriculum=false&search_all_class_year=false',
    'https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_class&selected_year=2564&selected_semester=2&selected_faculty=01&selected_department=05&selected_curriculum=06&selected_class_year&search_all_faculty=false&search_all_department=false&search_all_curriculum=false&search_all_class_year=true', # 
    'https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_subject_owner_id&selected_year=2564&selected_semester=2&selected_faculty=01&search_all_faculty=false&selected_subject_owner_id=6', # ภาษา
    'https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_subject_owner_id&selected_year=2564&selected_semester=2&selected_faculty=01&search_all_faculty=false&selected_subject_owner_id=10', # มนุษย์,
    'https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_subject_owner_id&selected_year=2564&selected_semester=2&selected_faculty=01&search_all_faculty=false&selected_subject_owner_id=9', # สังคม,
    'https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_subject_owner_id&selected_year=2564&selected_semester=2&selected_faculty=01&search_all_faculty=false&selected_subject_owner_id=21', # วิทย์,
  ]

  soups = []
  
  # Launch the browser
  if app.config['USE_LOCAL_HTML'] == True:

    for page_path in page_paths:
      md5_name  = hashlib.md5(page_path.encode())
      file_path = 'html_page/{}.html'.format(md5_name.hexdigest())

      with open(file_path, mode='r', encoding="utf-8") as f:
          soup  = BeautifulSoup(f, 'html.parser')
          soups.append(soup)
          f.close()

  else:
    # fixed single thread
    browser = await launch(
      handleSIGINT=False,
      handleSIGTERM=False,
      handleSIGHUP=False
    )

    for page_path in page_paths:
      page          = await browser.newPage()
      md5_name      = hashlib.md5(page_path.encode())
      file_path     = 'html_page/{}.html'.format(md5_name.hexdigest())

      await page.goto(page_path, {'waitUntil': 'networkidle0'})
      page_content  = await page.content()

      soup          = BeautifulSoup(page_content, 'html.parser', from_encoding="iso-8859-8")
      soups.append(soup)

      await page.screenshot({ "path": 'html_page/{}.png'.format(md5_name.hexdigest()), "fullPage": True }); 

      with open(file_path, mode='w', encoding="utf-8") as f:
        f.write(soup.prettify())
        f.close()

      await page.close()
      
    # Close browser
    await browser.close()

  regex = {
        "top"          : r'<main.*?<.*?<.*?<.*?<.*?<.*?<h2[^>]*>(?P<tableheader>.*?)</h2>.*?<h2[^>]*>(?P<semester>.*?)</h2></div><div[^>]*><div[^>]*>(?P<alltable>.*?)</div></div></div><div[^>]*><button.*?/button></div></div></div></div></main>',
        "all_subjects" : r'<div.*?><h2[^>]*>(?P<faculty>.*?)</h2><h2[^>]*>(?P<major>.*?)</h2><h2[^>]*>(?P<field>.*?)</h2>(?P<field_subjects>.*?)</div><div class="v-card__actions">.*?</div></div>',
        "courses"      : r'<div><div[^>]*>(?P<type>.*?)</div><div[^>]*><div[^>]*><table>(?P<courses>.*?)</table></div></div></div>',
        "tbody"        : r"<tbody.*?/tbody>",
        "rowData"      : r'<tr.*?/tr>',
        "data"         : r'<td><div><.*?>(?P<courseID>\s*|\d*)</.*?></div></td><td><a[^>]*>(?P<courseName>\s*|\w+[\s\w]*\w+)</a></td><td>(?P<credit>\s*|\d{1}\(\d{1,2}-\d{1,2}-\d{1,2}\))</td><td[^>]*>(?P<section>\s*|\d+)<span>(?P<typediv>.*?)</span></td><td[^>]*><a[^>]*>(?P<schedule_all>.*?)</a></td><td>(?P<room>.*?)</td><td>(?P<building>.*?)</td><td[^>]*><div>(?P<teacher>.*?)</div></td><td[^>]*>(?P<exam>.*?)</td><td.*?v>(?P<restriction>.*?)</div></td><td.*?v>(?P<note>.*?)<.*?></td>',
        "type"         : r'<.*?>(?P<type>[\u0E00-\u0E7F]*)</span></span>',
        "exam"         : r'<div><span.*?<span.*?<span[^>]*>(?P<midterm>.*?)</span></div><div><span.*?<span.*?<span[^>]*>(?P<final>.*?)</span></div>',
        "teacher"      : r'<div>(.*?)</div>',
        "schedule"     : r'<div>(?P<schedule>[+ ]{,2}[\u0E00-\u0E7F]{1,2}. \d{2}:\d{2}-\d{2}:\d{2})</div>',
        "restriction"  : r'<div>(.*?)<div.*?/div></div>'
      }

  payloads        = []
  for soup in soups:
    payload       = {}
    minify_string = re.sub(r'(?s)<!--.*?-->|\s{3,}|\n', '', str(soup.prettify()))

    # get the semester data
    top                 = re.search(regex['top'], str(minify_string))
    payload["semester"] = top.group('semester')
    all_subjects = re.findall(regex['all_subjects'], top.group('alltable'))
    payload["subjects"] = []

    for field_table in all_subjects:
        fs = {
          "faculty": field_table[0],
          "major": field_table[1],
          "field": field_table[2],
          "field_subjects": []
        }

        courses_tables = re.findall(regex['courses'], field_table[3])

        for course_table in courses_tables:
            t = {
              "type": course_table[0],
              "courses": []
            }

            courses = re.findall(regex["tbody"], course_table[1])

            for course in courses:
                rows = re.findall(regex["rowData"], course)

                for row in rows:
                    
                    data                = {}
                    data_rex            = re.search(regex["data"], row)

                    data['courseId']    = data_rex.group('courseID')
                    data['courseName']  = data_rex.group('courseName')
                    data['credit']      = data_rex.group('credit')
                    data['section']     = data_rex.group('section')

                    if data_rex.group('typediv') != '':
                        data['type']    = re.search(
                            regex['type'], data_rex.group('typediv')).group('type')
                    else:
                        data['type']    = ""

                    data['schedule']    = re.findall(
                        regex['schedule'], data_rex.group('schedule_all'))

                    data['room']        = data_rex.group('room')
                    data['building']    = data_rex.group('building')

                    data['teacher']     = re.findall(
                        regex['teacher'], data_rex.group('teacher'))

                    if data_rex.group('exam') != '':
                        exam            = re.search(regex['exam'], data_rex.group('exam'))
                        data['midterm'] = exam.group('midterm')
                        data['final']   = exam.group('final')
                    else:
                        data['midterm'] = ""
                        data['final']   = ""

                    data['restriction'] = re.findall(
                        regex['restriction'], data_rex.group('restriction'))
                    data['note']        = data_rex.group('note')

                    t['courses'].append(data)

            fs['field_subjects'].append(t)

        payload['subjects'].append(fs)
    payloads.append(payload)
  return payloads

def toTableModel(tablesObj):
  courses     = []

  for tableObj in tablesObj:
    data           = tableObj
    ## input: 2 / 2564
    semester, year = re.split('/', data['semester'])
    semester       = semester.strip()
    year           = year.strip()
    for subject in data['subjects']:

      # "field": "วิศวกรรมคอมพิวเตอร์ ชั้นปีที่ 1", 
      field        = subject['field']
      if(field[-1].isnumeric()):
        class_year = field[-1]
      else:
        class_year = '0'

      for field_subject in subject['field_subjects']:
        for course in field_subject['courses']:
          # if(course['courseId'] == "90201012"):
          #   print(json.dumps(course, ensure_ascii=False))
          
          ## remove duplicate course
          found     = False
          for x in courses:
            if x.id == course['courseId']:
              for sec in x.section:
                if sec['type'] == course['type'] and sec['id'] == course['section']:
                  found = True
                  break
              if found:
                break

          if found:
            continue
    
          ## Modify final field
          final = date_new_format(course['final'])

          ## Modify midterm field
          midterm = date_new_format(course['midterm'])

          ## Modify schedule field
          new_schedule = []

          if len(course['schedule']) >= 1:
            for w in range(week_count):
              # ['ศ. 09:00-12:00']
              _d             = course['schedule'][0].split(" ")
              _idx_day       = daysThai2.index(_d[0])
              _t             = _d[1].split("-")
              _t_start       = _t[0].split(":")
              _t_end         = _t[1].split(":")
              _tmp_day       = start_date + timedelta(days=(w*7) + _idx_day)
              _tmp_day_start = _tmp_day.replace(minute=int(_t_start[1]), hour=int(_t_start[0]))
              _tmp_day_end   = _tmp_day.replace(minute=int(_t_end[1]), hour=int(_t_end[0]))
              # print(_tmp_day_start, _tmp_day_end)
              new_schedule.append({
                "start": int(_tmp_day_start.timestamp()),
                "end": int(_tmp_day_end.timestamp())
              })
          
          if len(course['schedule']) == 2:
            for w in range(week_count):
              # [
              # "พฤ. 17:00-18:30",
              # "+ พฤ. 18:45-20:15" <-- process only this line
              # ]
              _d             = course['schedule'][1].split(" ")[1:] # pop "+"
              _idx_day       = daysThai2.index(_d[0])
              _t             = _d[1].split("-")
              _t_start       = _t[0].split(":")
              _t_end         = _t[1].split(":")
              _tmp_day       = start_date + timedelta(days=(w*7) + _idx_day)
              _tmp_day_start = _tmp_day.replace(minute=int(_t_start[1]), hour=int(_t_start[0]))
              _tmp_day_end   = _tmp_day.replace(minute=int(_t_end[1]), hour=int(_t_end[0]))
              # print(_tmp_day_start, _tmp_day_end)
              new_schedule.append({
                "start": int(_tmp_day_start.timestamp()),
                "end": int(_tmp_day_end.timestamp())
              })

          course['schedule'] = new_schedule

          course_type = find_course_type(course['courseId'])

          dup = False
          for c in courses:
            if c.get_id() == course['courseId']:
              dup = True
              c.section.append({
                "id": course['section'],
                "schedule": course['schedule'],
                "room": course['room'],
                "building": course['building'],
                "type": course['type']
              })
              break

          if not dup:
            courses.append(Course(**{**course, 'class_year': class_year, 'midterm': midterm, 'final': final, 'course_type': course_type, "semester": semester, "year": year}))
  
  return courses

async def cacheCheck():
  global timestamp
  global data
  # print(time.time() - timestamp, minuteToMilSecond(cacheing_time))
  if(time.time() - timestamp > minuteToMilSecond(cacheing_time)):
    timestamp = time.time()
    data = await fetchNewHTML()
    data = toTableModel(data)
  else:
    pass
  
async def findById(id):
  await cacheCheck()
  global data
  results = []
  for course in data:
    if course.id == id:
      results.append(course)
  
  return results

async def tableCaching():
  await cacheCheck()
  global data
  return data