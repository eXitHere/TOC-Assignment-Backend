const helloWorld = require('../utils/test');
const callScript = require('../utils/callScript');
const { getValue } = require('../utils/caching');

exports.test = async (req, res) => {
  res.status(200).send(await getValue());
};

exports.testScript = async (req, res) => {
  res.status(200).send({ jsonResponse: await callScript.test() });
};
