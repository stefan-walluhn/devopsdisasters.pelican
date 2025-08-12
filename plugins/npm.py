import logging
import os
import shutil
import subprocess
from pelican import signals
from pelican.generators import Generator


log = logging.getLogger(__name__)


class NpmStaticGenerator(Generator):
    def __init__(self, context, settings, path, theme, output_path, **kwargs):
        self.npm_tmp_modules = settings.get('NPM_TMP_PATH', 'node_modules')
        self.npm_target_modules = os.path.join(
            output_path, settings.get('NPM_TARGET_PATH', 'node_modules')
        )
        self.npm_executable = settings.get('NPM_EXECUTABLE', 'npm')
        self.npm_args = settings.get(
            'NPM_ARGS',
            ['--production', '--frozen-lockfile', '--silent']
        )

        super(NpmStaticGenerator, self).__init__(
            context, settings, path, theme, output_path, **kwargs
        )

    def generate_context(self):
        try:
            subprocess.run(
                [
                    self.npm_executable, 'install',
                    *self.npm_args
                ],
                capture_output=True,
                check=True,
                encoding='utf-8'
            )
        except subprocess.CalledProcessError as e:
            log.error('npm failed: %s', e.stderr)
            raise e

        log.debug('npm succeeded')

    def generate_output(self, writer):
        shutil.copytree(self.npm_tmp_modules, self.npm_target_modules,
                        ignore=shutil.ignore_patterns('.*'),
                        dirs_exist_ok=True)


def get_generators(pelican_object):
    return NpmStaticGenerator


def register():
    signals.get_generators.connect(get_generators)
