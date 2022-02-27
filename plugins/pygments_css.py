import os
from pelican import signals
from pelican.generators import Generator
from pygments.formatters import HtmlFormatter


class PygmentsCSSGenerator(Generator):
    def generate_output(self, writer):
        with open(os.path.join(self.output_path, 'pygments.css'), 'w') as css:
            css.write(HtmlFormatter().get_style_defs('.highlight'))


def get_generators(pelican_object):
    return PygmentsCSSGenerator


def register():
    signals.get_generators.connect(get_generators)
