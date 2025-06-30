import os

from flask import Flask, request, session, redirect, url_for
from flask_babel import Babel

babel = Babel()

def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(['en', 'sk'])

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        BABEL_TRANSLATION_DIRECTORIES=os.path.join(app.root_path, 'translations')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    babel.init_app(app, locale_selector=get_locale)
    app.jinja_env.add_extension('jinja2.ext.i18n')

    @app.route('/language/<language>')
    def set_language(language):
        if language in app.config['LANGUAGES']:
            session['language'] = language
        return redirect(request.referrer or url_for('index'))

    from . import db, auth, blog
    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    app.add_url_rule('/', endpoint='index')

    return app