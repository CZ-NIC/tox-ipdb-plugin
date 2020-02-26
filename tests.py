"""Tests for tox_ipdb plugin."""
import unittest
from unittest.mock import sentinel

from tox.config import Config, DepConfig, Parser, TestenvConfig

from tox_ipdb import tox_configure


class TestToxConfigure(unittest.TestCase):
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
