const express = require('express');
const multer = require('multer');
const Router = express.Router();
const transcriptController = require('./controller/transcript.controller');
const tableController = require('./controller/table.controller');

const upload = multer();

Router.post(
  '/uploadTranscript',
  upload.single('file'),
  transcriptController.uploadTranscript
);

// ? type=วิชาบังคับ
Router.get('/tables', tableController.fetchTable);

module.exports = Router;
