const helloWorld = require('../utils/test');

exports.test = (req, res) => {
  res.status(200).send(helloWorld.say());
};
