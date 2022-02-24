import logging
import shutil
import subprocess
from pelican import signals
from pelican.generators import Generator


log = logging.getLogger(__name__)


class YarnStaticGenerator(Generator):
    def __init__(self, context, settings, path, theme, output_path, **kwargs):
        self.node_modules = settings.get('NODE_MODULES_PATH', 'node_modules')
        self.yarn_executable = settings.get('YARN_EXECUTABLE', '/usr/bin/yarn')
        self.yarn_args = settings.get('YARN_ARGS',
                                      ['--modules-folder', self.node_modules,
                                       '--production',
                                       '--silent'])

        super(YarnStaticGenerator, self).__init__(
            context, settings, path, theme, output_path, **kwargs
        )

    def generate_context(self):
        subprocess.run([self.yarn_executable, 'install', *self.yarn_args])

    def generate_output(self, writer):
        shutil.copytree(self.node_modules, self.output_path,
                        ignore=shutil.ignore_patterns('.*'),
                        dirs_exist_ok=True)


def get_generators(pelican_object):
    return YarnStaticGenerator


def register():
    signals.get_generators.connect(get_generators)
