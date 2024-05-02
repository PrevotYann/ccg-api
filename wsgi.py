import os, sys

# Environment setup
virtenv = os.path.expanduser('~') + '/venv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    if sys.version.split(' ')[0].split('.')[0] == '3':
        exec(compile(open(virtualenv, "rb").read(), virtualenv, 'exec'), dict(__file__=virtualenv))
    else:
        execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass

sys.path.append(os.path.expanduser('~'))
sys.path.append(os.path.expanduser('~') + '/ROOT/')

# Importing and wrapping the ASGI app with ASGIMiddleware to make it WSGI compatible
from main import app
from a2wsgi import ASGIMiddleware

application = ASGIMiddleware(app)