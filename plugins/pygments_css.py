import os
from pelican import signals
from pelican.generators import Generator
from pygments.formatters import HtmlFormatter


class PygmentsCSSGenerator(Generator):
    def __init__(self, context, settings, path, theme, output_path, **kwargs):
        self.style = settings.get('PYGMENTS_STYLE', 'default')

        super(PygmentsCSSGenerator, self).__init__(
            context, settings, path, theme, output_path, **kwargs
        )

    def generate_output(self, writer):
        with open(os.path.join(self.output_path, 'pygments.css'), 'w') as css:
            css.write(
                HtmlFormatter(style=self.style).get_style_defs('.highlight')
            )


def get_generators(pelican_object):
    return PygmentsCSSGenerator


def register():
    signals.get_generators.connect(get_generators)
