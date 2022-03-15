const helloWorld = require('../utils/test');
const callScript = require('../utils/callScript');

exports.test = (req, res) => {
  res.status(200).send(helloWorld.say());
};

exports.testScript = async (req, res) => {
  res.status(200).send({ jsonResponse: await callScript.test() });
};
