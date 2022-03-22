const path = require('path');
const fs = require('fs');

module.exports = async () => {
  const rawData = fs.readFileSync(
    path.resolve(__dirname, `../tmp/out_from_table_scraped.txt`),
    'utf-8'
  );
  const json = JSON.parse(rawData);
  const semester = json.semester;
  const tables = json.subjects.find(
    ({ major, field }) =>
      major === 'วิศวกรรมคอมพิวเตอร์' &&
      field === 'วิศวกรรมคอมพิวเตอร์ ชั้นปีที่ 3'
  );

  const { field_subjects, faculty, major, field } = tables;

  return { semester, field_subjects, faculty, major, field };
};
