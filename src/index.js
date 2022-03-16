const express = require('express');
const routes = require('./routes');
const multer = require('multer');
const { text } = require('express');
const app = express();
const PORT = process.env.PORT || 3500;
const fs = require('fs');
app.use(express.json());

app.use('/api', routes);

// <---------------------------------------------------SAVE FILE --------------------------------------->
// const storage = multer.diskStorage({
//   destination: (req, file, cb) => {
//     cb(null, '.');
//   },
//   filename: (req, file, cb) => {
//     cb(
//       null,
//       'file-' +
//         Date.now() +
//         '.' +
//         file.originalname.split('.')[file.originalname.split('.').length - 1]
//     );
//   },
// });

// <---------------------------------------------------READFILE --------------------------------------->
const upload = multer();
app.post('/upload', upload.single('file'), function (req, res) {
  console.log(req.file, req.body);
  console.log('req.file.buffer', req.file.buffer.toString());
  res.status(200).send(req.file.buffer.toString());
});

app.listen(PORT, () => {
  console.log(`server is listening on port ${PORT}`);
});
