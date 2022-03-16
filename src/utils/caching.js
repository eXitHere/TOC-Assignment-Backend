const axios = require('axios');

let data = {
  value: {},
  timestamp: 0,
};

// cache 5 minute
const MINUTE = 5;

const minuteToMilSecond = (min) => {
  return min * 60 * 1000;
};

const fetchHTML = async () => {
  try {
    const url = 'https://www.google.com';
    const res = await axios.get(url);

    // check response is html
    if (res.data.toString().startsWith('<!doctype html>')) {
      return res.data;
    }
  } catch (error) {
    console.log(error);
  }
  return '';
};

const processHTMLToJson = async (html) => {
  // TODO: Call python script
  return [
    { name: 'วิชาอะไรวะ', id: '62000000' },
    {
      name: 'วิชาอะไรอีกแล้วว',
      id: '63000000',
    },
  ];
};

exports.getValue = async () => {
  if (new Date().getTime() - data.timestamp > minuteToMilSecond(MINUTE)) {
    data.timestamp = new Date().getTime(); // set new timestamp
    const html = await fetchHTML();
    data.value = await processHTMLToJson(html);
    console.log('fetch new Data');
  } else {
    console.log('using cache');
  }

  return data.value;
};
