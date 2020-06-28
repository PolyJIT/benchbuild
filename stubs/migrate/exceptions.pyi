class Error(Exception): ...
class ApiError(Error): ...
class KnownError(ApiError): ...
class UsageError(ApiError): ...
class ControlledSchemaError(Error): ...
class InvalidVersionError(ControlledSchemaError): ...
class VersionNotFoundError(KeyError): ...
class DatabaseNotControlledError(ControlledSchemaError): ...
class DatabaseAlreadyControlledError(ControlledSchemaError): ...
class WrongRepositoryError(ControlledSchemaError): ...
class NoSuchTableError(ControlledSchemaError): ...
class PathError(Error): ...
class PathNotFoundError(PathError): ...
class PathFoundError(PathError): ...
class RepositoryError(Error): ...
class InvalidRepositoryError(RepositoryError): ...
class ScriptError(Error): ...
class InvalidScriptError(ScriptError): ...
class InvalidVersionError(Error): ...
class NotSupportedError(Error): ...
class InvalidConstraintError(Error): ...
class MigrateDeprecationWarning(DeprecationWarning): ...
