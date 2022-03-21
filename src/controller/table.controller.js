const readJsonString = require('../utils/readJsonString');

exports.fetchTable = async (req, res) => {
  let { type } = req.query;
  // วิชาเลือก / วิชาเลือกเฉพาะสาขา, วิชาบังคับ
  console.log(type);
  const tables = await readJsonString();

  if (!type) {
    type = 'วิชาบังคับ';
    res.send(tables.field_subjects);
    return;
  }
  // console.log(type);
  const table = tables.field_subjects?.find((t) => t.type === type);
  // console.log(table);
  res.send([table]);
};
