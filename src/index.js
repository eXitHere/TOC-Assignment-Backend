const express = require('express');
const routes = require('./routes');
const multer = require('multer');
const app = express();
const PORT = process.env.PORT || 3500;

app.use(express.json());

app.use('/api', routes);

app.listen(PORT, () => {
  console.log(`server is listening on port ${PORT}`);
});
