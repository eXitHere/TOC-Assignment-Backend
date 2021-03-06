const pdfParse = require('pdf-parse');
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
// const upload = multer();
// app.post('/upload', upload.single('file'), function (req, res) {
//   console.log(req.file, req.body);

//   console.log('req.file.buffer', req.file.buffer.toString());
//   res.status(200).send(req.file.buffer.toString());
// });

exports.uploadTranscript = async (req, res) => {
  // console.log('req.file.buffer', req.file.buffer.toString());
  if (!req.file) {
    return res.status(400).send({ error: 'กรุณาอัพโหลดไฟล์' });
  }
  // parse text from pdf

  const textFromPDF = await pdfParse(req.file.buffer);
  res.status(200).send(textFromPDF.text);

  // TODO: Call python script
};
