AUTHOR = 'Stefan'
SITENAME = 'Devops Disasters'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Berlin'

DEFAULT_LANG = 'de'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_PAGINATION = 10

STATIC_PATHS = ['static']
EXTRA_PATH_METADATA = {
    'static/favicon.ico': {'path': 'favicon.ico'},
}

PLUGIN_PATHS = ['plugins']
PLUGINS = ['pygments_css', 'yarn']

YARN_TARGET_PATH = 'js'

PYGMENTS_STYLE = 'tango'
