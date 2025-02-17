from typing import TypeVar, Generic, Never, assert_never
from dataclasses import dataclass
from enum import StrEnum, auto

T = TypeVar('T')

class ConfigSource(StrEnum):
    FILE = auto()
    ENV = auto()
    DEFAULT = auto()

@dataclass(frozen=True, slots=True)
class ConfigValue(Generic[T]):
    value: T
    source: ConfigSource
    timestamp: float
    version: str

class ConfigManager:
    def get_config_value[T](self, key: str, default: T) -> ConfigValue[T]:
        """Enhanced generic type handling in Python 3.13."""
        match self._get_source(key):
            case ConfigSource.FILE:
                return self._load_from_file(key, default)
            case ConfigSource.ENV:
                return self._load_from_env(key, default)
            case ConfigSource.DEFAULT:
                return ConfigValue(default, ConfigSource.DEFAULT, time.time(), "1.0.0")
            case _:
                assert_never(self._get_source(key))

    def _get_source(self, key: str) -> ConfigSource:
        """Determine configuration source."""
        if self._exists_in_file(key):
            return ConfigSource.FILE
        if self._exists_in_env(key):
            return ConfigSource.ENV
        return ConfigSource.DEFAULT