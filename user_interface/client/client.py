from flask import Flask, send_from_directory

app = Flask(__name__)


@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
  return send_from_directory('./dist', path)


@app.route('/')
def root():
  return send_from_directory('./dist', 'index.html')


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)


@app.errorhandler(500)
def server_error(e):
  return 'An internal error occurred [client.py] %s' % e, 500