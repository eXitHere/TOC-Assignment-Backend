from app import app
if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.config['USE_LOCAL_HTML'] = True
    # app.run(port=8000, debug=True)
    app.run(host='0.0.0.0', port=8000)