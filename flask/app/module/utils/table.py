# -*- coding: utf-8 -*-

import time
from pyppeteer import launch
from bs4 import BeautifulSoup
import re

timestamp = 0
cacheing_time = 5 # minutes
data = {}

def minuteToMilSecond(min):
  return min * 60

async def fetchNewHTML():
  # Launch the browser
  browser = await launch(
    handleSIGINT=False,
    handleSIGTERM=False,
    handleSIGHUP=False
  )

  # Open a new browser page
  page = await browser.newPage()

  # Create a URI for our test file
  page_path = 'https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_class&selected_year=2564&selected_semester=2&selected_faculty=01&selected_department=05&selected_curriculum=06&selected_class_year=3&search_all_faculty=false&search_all_department=false&search_all_curriculum=false&search_all_class_year=false'

  # Open our test file in the opened page
  await page.goto(page_path, {'waitUntil': 'networkidle0'})
  page_content = await page.content()

  # Process extracted content with BeautifulSoup
  soup = BeautifulSoup(page_content, 'html.parser', from_encoding="iso-8859-8")
  # print(soup.span.string)

  # Close browser
  await browser.close()

  regex = {
        "top": r'<main.*?<.*?<.*?<.*?<.*?<.*?<h2[^>]*>(?P<tableheader>.*?)</h2>.*?<h2[^>]*>(?P<semester>.*?)</h2></div><div[^>]*><div[^>]*>(?P<alltable>.*?)</div></div></div><div[^>]*><button.*?/button></div></div></div></div></main>',

        "all_subjects": r'<div.*?><h2[^>]*>(?P<faculty>.*?)</h2><h2[^>]*>(?P<major>.*?)</h2><h2[^>]*>(?P<field>.*?)</h2>(?P<field_subjects>.*?)</div><div class="v-card__actions">.*?</div></div>',

        "courses": r'<div><div[^>]*>(?P<type>.*?)</div><div[^>]*><div[^>]*><table>(?P<courses>.*?)</table></div></div></div>',

        "tbody": r"<tbody.*?/tbody>",

        "rowData": r'<tr.*?/tr>',

        "data": r'<td><div><span>(?P<courseID>\s*|\d*)</span></div></td><td><a[^>]*>(?P<courseName>\s*|\w+[\s\w]*\w+)</a></td><td>(?P<credit>\s*|\d{1}\(\d{1}-\d{1}-\d{1}\))</td><td[^>]*>(?P<section>\s*|\d+)<span><span[^>]*><span[^>]*>(?P<type>\s*|[\u0E00-\u0E7F]*)</span></span></span></td><td[^>]*><a[^>]*>[<div>]*(?P<schedule>.*?)[</div>]*</a></td><td>(?P<room>.*?)</td><td>(?P<building>.*?)</td><td[^>]*><div>(?P<teacher>.*?)</div></td><td.*?><span.*?/span><span[^>]*>(?P<midterm>.*?)</span>.*?<span.*?/span><span[^>]*>(?P<final>.*?)<.*?/td><td.*?v>(?P<restriction>.*?)</div></td><td.*?v>(?P<note>.*?)<.*?></td>',

        "teacher": r'<div>(.*?)</div>',

        "restriction": r'<div>(.*?)<div.*?/div></div>'
    }

  payload = {}

  soup = soup.prettify()
  print(soup)

  # minify html for making simpler regex
  minify_string = re.sub(r'(?s)<!--.*?-->|\s{3,}|\n', '', str(soup))
  # print(minify_string)
  
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

                  data_rex = re.search(regex["data"], row)

                  teacher_list = re.findall(
                      regex['teacher'], data_rex.group('teacher'))
                  condition_list = re.findall(
                      regex['restriction'], data_rex.group('restriction'))

                  data = data_rex.groupdict()

                  data['teacher'] = teacher_list
                  data['restriction'] = condition_list

                  t['courses'].append(data)

          fs['field_subjects'].append(t)

      payload['subjects'].append(fs)

  return payload

async def tableCaching():
  global timestamp
  global data

  # print(time.time() - timestamp, minuteToMilSecond(cacheing_time))
  if(time.time() - timestamp > minuteToMilSecond(cacheing_time)):
    print('fetch new')
    timestamp = time.time()
    data = await fetchNewHTML()
  else:
    print('using cache')
  return data