const express = require('express');
const Router = express.Router();
const testController = require('./controller/test.controller');

Router.get('/', testController.test);
Router.get('/test', testController.testScript);
// /api/subject/:type
// วิชาภาค
// วิชาเลือก

module.exports = Router;
