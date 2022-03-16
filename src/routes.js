const express = require('express');
const multer = require('multer');
const Router = express.Router();
const testController = require('./controller/test.controller');
const transcriptController = require('./controller/transcript.controller');

const upload = multer();

Router.get('/', testController.test);
Router.get('/test', testController.testScript);
Router.post(
  '/uploadTranscript',
  upload.single('file'),
  transcriptController.uploadTranscript
);
// Router.post('/upload', testController.testUpload);
// /api/subject/:type
// วิชาภาค
// วิชาเลือก

module.exports = Router;
