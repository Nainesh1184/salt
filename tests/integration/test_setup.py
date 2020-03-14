# -*- coding: utf-8 -*-
'''
tests.integration.test_setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# Import python libs
from __future__ import absolute_import, print_function, unicode_literals
import os
import re

# Import Salt Testing libs
from tests.support.runtests import RUNTIME_VARS
from tests.support.unit import skipIf
from tests.support.helpers import skip_if_not_root
from tests.support.virtualenv import VirtualEnvHelper

# Import salt libs
import salt.utils.path
import salt.utils.platform
from salt.modules.virtualenv_mod import KNOWN_BINARY_NAMES


@skip_if_not_root
@skipIf(salt.utils.path.which_bin(KNOWN_BINARY_NAMES) is None, 'virtualenv not installed')
class SetupTest(VirtualEnvHelper):
    '''
    Tests for building and installing packages using setup.py
    '''
    def test_wheel_build(self):
        '''
        test building a bdist_wheel package and ensure
        '''
        # Let's create the testing virtualenv
        self._create_virtualenv(self.venv_dir)
        ret = self.run_function('cmd.run', ['python setup.py bdist_wheel --dist-dir={0}'.format(self.venv_dir)], cwd=RUNTIME_VARS.CODE_DIR)

        for _file in os.listdir(self.venv_dir):
            if _file.endswith('whl'):
                whl = os.path.join(self.venv_dir, _file)
                break

        ret = self.run_function('pip.install', pkgs=whl, bin_env=self.venv_dir)

        # Let's ensure the version is correct
        pip_ver = self.run_function('pip.list', bin_env=self.venv_dir).get('salt')
        whl_ver = [x for x in whl.split('/')[-1:][0].split('-') if re.search(r'^\d.\d*', x)][0]
        assert pip_ver == whl_ver
