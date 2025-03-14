from enum import StrEnum


class VersionEnvironment(StrEnum):
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"
