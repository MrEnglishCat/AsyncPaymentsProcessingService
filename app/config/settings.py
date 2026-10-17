from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import BaseModel, PostgresDsn


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    payments: str = "/payments"
    outbox: str = "/outbox"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseConfig(BaseModel):
    NAME: str
    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str
    SQLITE_NAME: str
    echo: bool = True
    echo_pool: bool = False
    expire_on_commit: bool = False
    autocommit: bool = False
    autoflush: bool = False
    pool_size: int = 20
    max_over_flow: int = 10
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def DB_URL(self):
        return f"postgresql://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def TEST_DB_URL(self):
        return f"sqlite+aiosqlite:///{self.SQLITE_NAME}"


class FastStreamConfig(BaseModel): ...


class ProjectSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
    )
    faststream: FastStreamConfig = FastStreamConfig()
    db: DatabaseConfig
    api: ApiPrefix = ApiPrefix()
    run: RunConfig = RunConfig()

    MODE: str
    APP_AUTH_KEY: str


settings = ProjectSettings()
