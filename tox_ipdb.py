"""Tox plugin which installs ipdb in tox environments."""
import tox
from tox.action import Action
from tox.config import Config, DepConfig
from tox.venv import VirtualEnv

__version__ = '0.2'


@tox.hookimpl
def tox_configure(config: Config) -> None:
    """Add ipdb to dependencies of every tox environment."""
    for envconfig in config.envconfigs.values():
        envconfig.deps.append(DepConfig('ipdb'))


@tox.hookimpl
def tox_testenv_create(venv: VirtualEnv, action: Action) -> None:
    """Add tox-ipdb to provision venv."""
    if venv.name == venv.envconfig.config.provision_tox_env:
        # Add tox-ipdb-plugin itself into provision tox environment.
        venv.envconfig.deps.append(DepConfig('tox-ipdb-plugin'))
