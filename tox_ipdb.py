"""Tox plugin which installs ipdb in tox environments."""
import tox
from tox.config import Config, DepConfig

__version__ = '0.1'


@tox.hookimpl
def tox_configure(config: Config) -> None:
    """Add ipdb to dependencies of every tox environment."""
    for envconfig in config.envconfigs.values():
        envconfig.deps.append(DepConfig('ipdb'))
