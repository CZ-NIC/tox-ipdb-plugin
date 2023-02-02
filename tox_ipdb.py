"""Tox plugin which installs ipdb in tox environments."""
import logging
from distutils.version import LooseVersion

import tox

__version__ = '0.3'
_LOGGER = logging.getLogger(__name__)


if LooseVersion(tox.__version__) < LooseVersion('4.0.0'):
    # TOX 3
    from tox import hookimpl  # type: ignore[attr-defined]
    from tox.action import Action
    from tox.config import Config, DepConfig  # type: ignore[attr-defined]
    from tox.venv import VirtualEnv

    @hookimpl
    def tox_configure(config: Config) -> None:
        """Add ipdb to dependencies of every tox environment."""
        for envconfig in config.envconfigs.values():
            envconfig.deps.append(DepConfig('ipdb'))

    @hookimpl
    def tox_testenv_create(venv: VirtualEnv, action: Action) -> None:
        """Add tox-ipdb to provision venv."""
        if venv.name == venv.envconfig.config.provision_tox_env:
            # Add tox-ipdb-plugin itself into provision tox environment.
            venv.envconfig.deps.append(DepConfig('tox-ipdb-plugin'))

else:
    # TOX 4
    from tox.config.loader.api import Override
    from tox.config.of_type import _PLACE_HOLDER
    from tox.config.sets import EnvConfigSet
    from tox.plugin import impl
    from tox.session.state import State

    @impl
    def tox_add_env_config(env_conf: EnvConfigSet, state: State) -> None:
        """Ensure ipdb is in every tox environment."""
        if 'package_env' in state.conf.core and env_conf.name == state.conf.core['package_env']:
            # Skip package env
            _LOGGER.debug("tox-ipdb-plugin[%s]: Ignoring package environment.", env_conf.name)
            return

        old_deps = env_conf['deps'].lines()

        if env_conf.name == state.conf.core['provision_tox_env']:
            # It's a provision env, add the plugin itself.
            new_deps = old_deps + ['tox-ipdb-plugin']
            _LOGGER.debug("tox-ipdb-plugin[%s]: Appending tox-ipdb-plugin to provision environment dependencies.",
                          env_conf.name)
        else:
            # It's not a provision env, add ipdb.
            new_deps = old_deps + ['ipdb']
            _LOGGER.debug("tox-ipdb-plugin[%s]: Appending ipdb to environment dependencies.", env_conf.name)

        _LOGGER.debug("tox-ipdb-plugin[%s]: New deps: %s", env_conf.name, new_deps)

        override = Override('{}.deps={}'.format(env_conf.name, '\n'.join(new_deps)))
        env_conf.loaders[0].overrides[override.key] = override

        # Clear cache
        env_conf._defined['deps']._cache = _PLACE_HOLDER  # type: ignore[attr-defined]  # _cache is not public API
