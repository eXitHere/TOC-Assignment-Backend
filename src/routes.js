const express = require('express');
const Router = express.Router();
const testController = require('./controller/test.controller');

Router.get('/', testController.test);

module.exports = Router;
