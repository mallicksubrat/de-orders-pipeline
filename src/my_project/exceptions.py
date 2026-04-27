class ProjectError(Exception):
    """Base class for project-specific failures."""


class ConfigError(ProjectError):
    """Raised when configuration cannot be loaded or validated."""


class DataSourceError(ProjectError):
    """Raised when the extractor cannot read or understand source data."""


class TransformationError(ProjectError):
    """Raised when raw rows cannot be transformed into the canonical model."""


class DataQualityError(ProjectError):
    """Raised when transformed data violates quality expectations."""


class LoadError(ProjectError):
    """Raised when the warehouse load step fails."""
