import logging
import os
import shutil
import subprocess
from pelican import signals
from pelican.generators import Generator


log = logging.getLogger(__name__)


class YarnStaticGenerator(Generator):
    def __init__(self, context, settings, path, theme, output_path, **kwargs):
        self.yarn_tmp_modules = settings.get('YARN_TMP_PATH', 'node_modules')
        self.yarn_target_modules = os.path.join(
            output_path, settings.get('YARN_TARGET_PATH', 'node_modules')
        )
        self.yarn_executable = settings.get('YARN_EXECUTABLE', 'yarn')
        self.yarn_args = settings.get(
            'YARN_ARGS',
            ['--production', '--frozen-lockfile', '--silent']
        )

        super(YarnStaticGenerator, self).__init__(
            context, settings, path, theme, output_path, **kwargs
        )

    def generate_context(self):
        try:
            subprocess.run(
                [
                    self.yarn_executable, 'install',
                    '--modules-folder', self.yarn_tmp_modules,
                    *self.yarn_args
                ],
                capture_output=True,
                check=True,
                encoding='utf-8'
            )
        except subprocess.CalledProcessError as e:
            log.error('yarn failed: %s', e.stderr)
            raise e

        log.debug('yarn succeeded')

    def generate_output(self, writer):
        shutil.copytree(self.yarn_tmp_modules, self.yarn_target_modules,
                        ignore=shutil.ignore_patterns('.*'),
                        dirs_exist_ok=True)


def get_generators(pelican_object):
    return YarnStaticGenerator


def register():
    signals.get_generators.connect(get_generators)
