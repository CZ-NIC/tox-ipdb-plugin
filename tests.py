"""Tests for tox_ipdb plugin."""
from functools import partial
from pathlib import Path
from typing import List
from unittest import TestCase, skipUnless
from unittest.mock import sentinel

import tox

if tox.__version__ < '4':
    from tox.config import Config, DepConfig, Parser, TestenvConfig  # type: ignore[attr-defined]
    from tox.venv import VirtualEnv

    from tox_ipdb import tox_configure, tox_testenv_create
else:
    from tox.config.cli.parse import Options
    from tox.config.cli.parser import Parsed
    from tox.config.loader.memory import MemoryLoader
    from tox.config.main import Config
    from tox.config.source.ini import IniSource
    from tox.session.state import State
    from tox.tox_env.python.pip.req_file import PythonDeps

    from tox_ipdb import tox_add_env_config


@skipUnless(tox.__version__ < '4', "Test only for tox 3.")
class TestToxConfigure(TestCase):
    def test_empty_config(self):
        config = Config(sentinel.pluginmanager, sentinel.option, sentinel.interpreters, Parser(), sentinel.args)

        tox_configure(config)

        self.assertEqual(config.envconfigs, {})

    def test_empty_deps(self):
        env_config = TestenvConfig(sentinel.name, sentinel.config, sentinel.factors, sentinel.reader)
        env_config.deps = []
        config = Config(sentinel.pluginmanager, sentinel.option, sentinel.interpreters, Parser(), sentinel.args)
        config.envconfigs[sentinel.name] = env_config

        tox_configure(config)

        self.assertEqual(len(config.envconfigs[sentinel.name].deps), 1)
        self.assertEqual(config.envconfigs[sentinel.name].deps[0].name, 'ipdb')

    def test_deps(self):
        env_config = TestenvConfig(sentinel.name, sentinel.config, sentinel.factors, sentinel.reader)
        env_config.deps = [DepConfig('dummy')]
        config = Config(sentinel.pluginmanager, sentinel.option, sentinel.interpreters, Parser(), sentinel.args)
        config.envconfigs[sentinel.name] = env_config

        tox_configure(config)

        self.assertEqual(len(config.envconfigs[sentinel.name].deps), 2)
        self.assertEqual(config.envconfigs[sentinel.name].deps[0].name, 'dummy')
        self.assertEqual(config.envconfigs[sentinel.name].deps[1].name, 'ipdb')


@skipUnless(tox.__version__ < '4', "Test only for tox 3.")
class TestToxTestenvCreate(TestCase):
    def test_provision(self):
        config = Config(sentinel.pluginmanager, sentinel.option, sentinel.interpreters, Parser(), sentinel.args)
        config.provision_tox_env = '.tox'
        env_config = TestenvConfig('.tox', config, sentinel.factors, sentinel.reader)
        env_config.deps = []
        venv = VirtualEnv(env_config)

        self.assertIsNone(tox_testenv_create(venv, sentinel.action))

        self.assertEqual(len(env_config.deps), 1)
        self.assertEqual(env_config.deps[0].name, 'tox-ipdb-plugin')

    def test_other_env(self):
        config = Config(sentinel.pluginmanager, sentinel.option, sentinel.interpreters, Parser(), sentinel.args)
        config.provision_tox_env = '.tox'
        env_config = TestenvConfig(sentinel.name, config, sentinel.factors, sentinel.reader)
        env_config.deps = []
        venv = VirtualEnv(env_config)

        self.assertIsNone(tox_testenv_create(venv, sentinel.action))

        self.assertEqual(env_config.deps, [])


@skipUnless(tox.__version__ >= '4', "Test only for tox 4.")
class ToxAddEnvConfigTest(TestCase):
    def _test(self, env_name: str, initial_deps: str, result: List[str]) -> None:
        root = Path(__file__).parent
        source = IniSource(Path('/tmp/does/not/exist'), '')  # nosec
        parsed = Parsed(override=(), root_dir=root, work_dir=root)
        state = State(Options(parsed, None, source, sentinel.cmd_handlers, sentinel.tox_handler), [])

        # Copy from tox.provision
        state.conf.core.add_config(
            keys="provision_tox_env",
            of_type=str,
            default=".tox",
            desc="Name of the virtual environment used to provision a tox.",
        )
        # Based on tox.tox_env.runner
        state.conf.core.add_config(
            keys=["package_env"],
            of_type=str,
            default='.pkg',
            desc="tox environment used to package",
        )

        env_conf = state.conf.get_env(env_name, loaders=[MemoryLoader()])

        # Copy from tox.tox_env.python.virtual_env.package.cmd_builder
        env_conf.add_config(
            keys="deps",
            of_type=PythonDeps,
            factory=partial(PythonDeps.factory, root),
            default=PythonDeps(initial_deps, root),
            desc="Name of the python dependencies as specified by PEP-440",
        )

        tox_add_env_config(env_conf, state)

        self.assertEqual(env_conf['deps'].lines(), result)

    def test_package_empty(self):
        self._test('.pkg', "", [])

    def test_package(self):
        self._test('.pkg', "gazpacho>=42", ['gazpacho>=42'])

    def test_provision_empty(self):
        self._test('.tox', "", ['tox-ipdb-plugin'])

    def test_provision(self):
        self._test('.tox', "gazpacho>=42", ['gazpacho>=42', 'tox-ipdb-plugin'])

    def test_testenv_empty(self):
        self._test('py310', "", ['ipdb'])

    def test_testenv(self):
        self._test('py310', "gazpacho>=42", ['gazpacho>=42', 'ipdb'])
