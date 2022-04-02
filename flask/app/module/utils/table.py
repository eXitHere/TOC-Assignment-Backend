# -*- coding: utf-8 -*-

import time
from pyppeteer import launch
from bs4 import BeautifulSoup
from datetime import datetime
from app import app
import re
import hashlib
from os.path import exists
from ..model.course import Course
from .course import findCourseType

timestamp = 0
cacheing_time = 5 # minutes
data = {}

def minuteToMilSecond(min):
  return min * 60

async def fetchNewHTML():

  # Create a URI for our test file
  # page_path = 'https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_class&selected_year=2564&selected_semester=2&selected_faculty=01&selected_department=05&selected_curriculum=06&selected_class_year&search_all_faculty=false&search_all_department=false&search_all_curriculum=false&search_all_class_year=true'
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
      print('load file', page_path)
      with open(file_path, mode='r', encoding="utf-8") as f:
          # soup = BeautifulSoup(f.read(), 'html.parser', from_encoding="iso-8859-8")
          soup = BeautifulSoup(f, 'html.parser')
          soups.append(soup)
          # print(soup)
          f.close()

  else:
    browser = await launch(
      handleSIGINT=False,
      handleSIGTERM=False,
      handleSIGHUP=False
    )

    # Open our test file in the opened page
    for page_path in page_paths:
      page = await browser.newPage()
      md5_name  = hashlib.md5(page_path.encode())
      file_path = 'html_page/{}.html'.format(md5_name.hexdigest())
      print('fetch', page_path)
      await page.goto(page_path, {'waitUntil': 'networkidle0'})
      page_content = await page.content()
      # Process extracted content with BeautifulSoup
      soup = BeautifulSoup(page_content, 'html.parser', from_encoding="iso-8859-8")
      soups.append(soup)
      #print(soup.span.string)
      await page.screenshot({ "path": 'html_page/{}.png'.format(md5_name.hexdigest()), "fullPage": True });  
      # print(md5_name.hexdigest())
      with open(file_path, mode='w', encoding="utf-8") as f:
        f.write(soup.prettify())
        f.close()
      # force clear content
      await page.close()
      
    # Close browser
    await browser.close()

  regex = {
        "top": r'<main.*?<.*?<.*?<.*?<.*?<.*?<h2[^>]*>(?P<tableheader>.*?)</h2>.*?<h2[^>]*>(?P<semester>.*?)</h2></div><div[^>]*><div[^>]*>(?P<alltable>.*?)</div></div></div><div[^>]*><button.*?/button></div></div></div></div></main>',

        "all_subjects": r'<div.*?><h2[^>]*>(?P<faculty>.*?)</h2><h2[^>]*>(?P<major>.*?)</h2><h2[^>]*>(?P<field>.*?)</h2>(?P<field_subjects>.*?)</div><div class="v-card__actions">.*?</div></div>',

        "courses": r'<div><div[^>]*>(?P<type>.*?)</div><div[^>]*><div[^>]*><table>(?P<courses>.*?)</table></div></div></div>',

        "tbody": r"<tbody.*?/tbody>",

        "rowData": r'<tr.*?/tr>',

        "data": r'<td><div><.*?>(?P<courseID>\s*|\d*)</.*?></div></td><td><a[^>]*>(?P<courseName>\s*|\w+[\s\w]*\w+)</a></td><td>(?P<credit>\s*|\d{1}\(\d{1,2}-\d{1,2}-\d{1,2}\))</td><td[^>]*>(?P<section>\s*|\d+)<span>(?P<typediv>.*?)</span></td><td[^>]*><a[^>]*>(?P<schedule_all>.*?)</a></td><td>(?P<room>.*?)</td><td>(?P<building>.*?)</td><td[^>]*><div>(?P<teacher>.*?)</div></td><td[^>]*>(?P<exam>.*?)</td><td.*?v>(?P<restriction>.*?)</div></td><td.*?v>(?P<note>.*?)<.*?></td>',
        
        "type": r'<.*?>(?P<type>[\u0E00-\u0E7F]*)</span></span>',

        "exam": r'<div><span.*?<span.*?<span[^>]*>(?P<midterm>.*?)</span></div><div><span.*?<span.*?<span[^>]*>(?P<final>.*?)</span></div>',

        "teacher": r'<div>(.*?)</div>',

        "schedule": r'<div>(?P<schedule>[+ ]{,2}[\u0E00-\u0E7F]{1,2}. \d{2}:\d{2}-\d{2}:\d{2})</div>',

        "restriction": r'<div>(.*?)<div.*?/div></div>'
  }

  payloads = []

  for soup in soups:
    payload = {}

    minify_string = re.sub(
        r'(?s)<!--.*?-->|\s{3,}|\n', '', str(soup.prettify()))

    # get the semester data
    top = re.search(regex['top'], str(minify_string))
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
                    
                    data = {}
                    data_rex = re.search(regex["data"], row)

                    data['courseId'] = data_rex.group('courseID')
                    data['courseName'] = data_rex.group('courseName')
                    data['credit'] = data_rex.group('credit')
                    data['section'] = data_rex.group('section')

                    if data_rex.group('typediv') != '':
                        data['type'] = re.search(
                            regex['type'], data_rex.group('typediv')).group('type')
                    else:
                        data['type'] = ""

                    data['schedule'] = re.findall(
                        regex['schedule'], data_rex.group('schedule_all'))

                    data['room'] = data_rex.group('room')
                    data['building'] = data_rex.group('building')

                    data['teacher'] = re.findall(
                        regex['teacher'], data_rex.group('teacher'))

                    if data_rex.group('exam') != '':
                        exam = re.search(regex['exam'], data_rex.group('exam'))
                        data['midterm'] = exam.group('midterm')
                        data['final'] = exam.group('final')
                    else:
                        data['midterm'] = ""
                        data['final'] = ""

                    data['restriction'] = re.findall(
                        regex['restriction'], data_rex.group('restriction'))
                    data['note'] = data_rex.group('note')

                    t['courses'].append(data)

            fs['field_subjects'].append(t)

        payload['subjects'].append(fs)
    payloads.append(payload)
  return payloads

def toTableModel(tablesObj):
  courses = []
  daysThai = ['อาทิตย์', 'จันทร์', 'อังคาร', 'พุธ', 'พฤหัส', 'ศุกร์', 'เสาร์']
  monthThai = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']

  for tableObj in tablesObj:
    data = tableObj
    ## input: 2 / 2564
    semester, year = re.split('/', data['semester'])
    semester = semester.strip()
    year = year.strip()
    for subject in data['subjects']:

      # "field": "วิศวกรรมคอมพิวเตอร์ ชั้นปีที่ 1", 
      field = subject['field']
      if(field[-1].isnumeric()):
        class_year = field[-1]
      else:
        class_year = '0'
      # print(class_year)
      for field_subject in subject['field_subjects']:
        # print(field_subject['type'], field_subject['courses'])
        for course in field_subject['courses']:
          
          ## remove duplicate course
          found = False
          for x in courses:
            # print(x['courseId'], course['courseId'])
            if x == course:
              found = True
              # print('break!')
              break

          if found:
            continue

          # print(course['schedule'], course['courseName'])

          date_final_start   = ""
          date_final_end     = ""
          date_midterm_start = ""
          date_midterm_end   = ""
    
          ## Modify final field
          final = course['final'].split()
          # print(final, course['final'])
          ## "จัดสอบเอง"
          if(len(final) > 1):
            # ['จันทร์', '23', 'พ.ค.', '2022', '13:30', '-', '16:30']
            d = daysThai.index(final[0])
            m = monthThai.index(final[2])

            # ["13", "30"]
            time_final_start = final[4].split(":")
            time_final_end   = final[6].split(":")
            # print(int(time_[0]))

            date_final_start = datetime(year=int(final[3]), month=int(m), day=int(final[1]))
            date_final_start = date_final_start.replace(minute=int(time_final_start[1]), hour=int(time_final_start[0]))

            date_final_end = datetime(year=int(final[3]), month=int(m), day=int(final[1]))
            date_final_end = date_final_end.replace(minute=int(time_final_end[1]), hour=int(time_final_end[0]))
            final = {'start': date_final_start, 'end': date_final_end}
            # print(date_final_start, date_final_end)
          else:
            final = course['final']

          ## Modify midterm field
          midterm = course['midterm'].split()
          # print(midterm, course['midterm'])
          """
          TODO:
          check midterm and final datetime is correct ?
          """
          # break
          ## "จัดสอบเอง"
          if(len(midterm) > 1):
            # ['จันทร์', '23', 'พ.ค.', '2022', '13:30', '-', '16:30']
            d = daysThai.index(midterm[0])
            m = monthThai.index(midterm[2])
            # print(d,m)

            # ["13", "30"]
            time_midterm_start = midterm[4].split(":")
            time_midterm_end   = midterm[6].split(":")
            # print(int(time_[0]))
            # print("xxx", date_midterm_start, "yyy", date_midterm_end)
            # print(midterm[3], m, midterm[1])
            date_midterm_start = datetime(year=int(midterm[3]), month=int(m), day=int(midterm[1]))
            date_midterm_start = date_midterm_start.replace(minute=int(time_midterm_start[1]), hour=int(time_midterm_start[0]))

            date_midterm_end = datetime(year=int(midterm[3]), month=int(m), day=int(midterm[1]))
            date_midterm_end = date_midterm_end.replace(minute=int(time_midterm_end[1]), hour=int(time_midterm_end[0]))
            midterm = {'start': date_midterm_start, 'end': date_midterm_end}
            # print(date_midterm_end )
            # print(date_midterm_start, date_midterm_end)
          else:
            midterm = course['midterm']
          # print(course['final'], "\n",course['midterm'],"\n", final, "\n",midterm, final == midterm,"\n\n")

          # detection type with courseId
          """
          ภาษา    902xxxxx
          มนุษย์    903xxxxx
          สังคม    904xxxxx
          วิทย์     901xxxxx
          ภาค     010xxxxx
          """

          course_type = findCourseType(course['courseId'])
         

          # courses.append({**course, 'class_year': class_year, 'midterm': midterm, 'final': final, 'course_type': course_type})
          print(course)
          courses.append(Course(**{**course, 'class_year': class_year, 'midterm': midterm, 'final': final, 'course_type': course_type, "semester": semester, "year": year}))
  return courses

async def cacheCheck():
  global timestamp
  global data
  # print(time.time() - timestamp, minuteToMilSecond(cacheing_time))
  if(time.time() - timestamp > minuteToMilSecond(cacheing_time)):
    print('fetch new')
    timestamp = time.time()
    data = await fetchNewHTML()
    data = toTableModel(data)
  else:
    print('using cache')

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