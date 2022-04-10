class Course():
  
  # {'courseId': '90101002', 'courseName': 'MATHEMATICS IN DAILY LIFE', 'credit': '3(3-0-6)', 'section': '101', 'type': 'ทฤษฎี', 
  # 'schedule': ['ศ. 09:00-12:00'], 'room': 'Online', 'building': 'อาคาร Online', 'teacher': ['ดร.งามเฉิด ด่านพัฒนามงคล'], 
  # 'midterm': 'พฤหัส 10 มี.ค. 2022 09:30 - 12:30', 'final': 'พฤหัส 12 พ.ค. 2022 09:30 - 12:30', 'restriction': [], 
  # 'note': 'ช่องทางการติดต่ออาจารย์ผู้สอน http://gened.kmitl.ac.th/2021/12/07/online-2-64/'}
  def __init__(self, type, courseName, courseId, credit, section, schedule, room, building, teacher, midterm, final, restriction, note, class_year, course_type, semester, year):
    # self.type         = type
    # self.name         = courseName
    # self.id           = courseId
    # self.credit       = credit
    # self.section      = section
    # self.schedule     = schedule
    # self.room         = room
    # self.building     = building
    # self.teacher      = teacher
    # self.midterm      = midterm
    # self.final        = final
    # self.restriction  = restriction
    # self.note         = note
    # self.class_year   = class_year
    # self.course_type  = course_type
    # self.semester     = semester
    # self.year         = year
    self.name         = courseName
    self.id           = courseId
    self.credit       = credit
    self.section      = [
      {
        "id": section,
        "schedule": schedule,
        "room": room,
        "building": building,
        "type": type
      }
    ]
    self.teacher      = teacher
    self.midterm      = midterm
    self.final        = final
    self.restriction  = restriction
    self.note         = note
    self.class_year   = class_year
    self.course_type  = course_type
    self.semester     = semester
    self.year         = year

  def get_id(self):
    return self.id

  def to_dict(self):
    return dict(
                name=self.name, 
                id=self.id, 
                # credit=self.credit, 
                # section=self.section, 
                # teacher=self.teacher, 
                # midterm=self.midterm, 
                # final=self.final, 
                # restriction=self.restriction,
                # note=self.note, 
                # class_year=self.class_year, 
                # course_type=self.course_type, 
                # semester=self.semester,
                # year=self.year
                )