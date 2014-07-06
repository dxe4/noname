from bottle import route, run, static_file

@route('/hello')
def hello():
    return "Hello World!"

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

run(host='localhost', port=8080, debug=True)
