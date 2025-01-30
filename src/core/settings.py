import os
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DBSettings(BaseSettings):
    name: str = Field(..., validation_alias='DB_NAME')
    user: str = Field(..., validation_alias='DB_USER')
    password: str = Field(..., validation_alias='DB_PASSWORD')
    host: str = Field(..., validation_alias='DB_HOST')
    port: int = Field(..., validation_alias='DB_PORT')

    @property
    def uri(self) -> str:
        return (f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}'
                f':{self.port}/{self.name}')

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

class JWTSettings(BaseSettings):
    secret_key: str = Field(..., min_length=8, max_length=64, validation_alias='JWT_SECRET_KEY')
    algorithm: str = Field(..., max_length=64, validation_alias='JWT_ALGORITHM')

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')


class RabbitMQSettings(BaseSettings):
    host: str = Field(..., validation_alias='RABBITMQ_HOST')

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')



class FernetConfiguration(BaseSettings):
    fernet_key: str = Field(..., validation_alias='FERNET_KEY')  # Ключ от шифрование
    fernet_IV: str = Field(..., validation_alias='FERNET_IV')  # IV

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

class Settings(BaseSettings):
    database_settings: DBSettings = DBSettings()
    fernet_settings: FernetConfiguration = FernetConfiguration()
    jwt_settings: JWTSettings = JWTSettings()
    rabbit_settings: RabbitMQSettings = RabbitMQSettings()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')


settings = Settings(_env_file='../../.env')
