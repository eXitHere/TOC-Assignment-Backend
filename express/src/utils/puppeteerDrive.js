const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

function objectToParam(params) {
  let param = '';
  let name = '';
  for (const key in params) {
    param += `${key}=${params[key]}&`;
    name += `${params[key]}_`;
  }
  return { param: param.slice(0, -1), name: name.slice(0, -1) };
}

async function scrape() {
  const params = {
    mode: 'by_class',
    selected_year: '2564',
    selected_semester: '2',
    selected_faculty: '01',
    selected_department: '05',
    selected_curriculum: '06',
    selected_class_year: '3',
    search_all_faculty: 'false',
    search_all_department: 'false',
    search_all_curriculum: 'false',
    search_all_class_year: 'false',
  };

  const { param, name } = objectToParam(params);
  // console.log(param);
  const browser = await puppeteer.launch({});
  const page = await browser.newPage();

  const uri = `https://new.reg.kmitl.ac.th/reg/#/teach_table?${param}`;
  console.log(`filename: ${name}.txt, uri: ${uri}`);
  // https://new.reg.kmitl.ac.th/reg/#/teach_table?mode=by_class&selected_year=2564&selected_semester=2&selected_faculty=01&selected_department=05&selected_curriculum=06&selected_class_year=3&search_all_faculty=false&search_all_department=false&search_all_curriculum=false&search_all_class_year=false

  await page.goto(uri, {
    waitUntil: 'networkidle0',
  });

  const data = await page.evaluate(
    () => document.querySelector('body').outerHTML
  );

  console.log(data);

  fs.writeFileSync(
    path.resolve(__dirname, `../tmp/${name}.txt`),
    data,
    'utf-8'
  );

  // console.log(data);
  await browser.close();
}

// scrape();

// module.exports = scrape;
