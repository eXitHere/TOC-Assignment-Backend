const express = require('express');
const fs = require('fs');
const Router = express.Router();
const testController = require('./controller/test.controller');

Router.get('/', testController.test);
Router.get('/test', testController.testScript);

module.exports = Router;
