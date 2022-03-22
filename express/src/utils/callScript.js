const { PythonShell } = require('python-shell');
const path = require('path');

module.exports = {
  test: async () => {
    let options = {
      mode: 'text',
      pythonOptions: ['-u'], // get print results in real-time
      scriptPath: path.join(__dirname, '../python'), //If you are having python_test.py script in same folder, then it's optional.
      args: ['fake_html_data'], //An argument which can be accessed in the script using sys.argv[1]
    };

    const result = await new Promise((resolve, reject) => {
      PythonShell.run('echo.py', options, (err, results) => {
        if (err) return reject(err);
        const val = results.toString();
        const json = JSON.parse(val);
        // console.log(json);
        return resolve(json);
      });
    });

    console.log(result);

    return result;
  },
};
