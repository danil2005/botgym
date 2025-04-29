from dataclasses import dataclass
from dotenv import load_dotenv
import os


@dataclass(frozen=True)
class TgBot:
    token: str


@dataclass(frozen=True)
class DataBase:
    host: str
    port: int
    user: str
    password: str
    name_db: str


@dataclass(frozen=True)
class Redis:
    host: str
    port: int
    password: str


@dataclass(frozen=True)
class Config:
    tg_bot: TgBot
    type_db: str
    data_base: DataBase = None
    redis: Redis = None


def load_config() -> Config:
    """Функция возвращает объект с переменными окружениями, необходимыми для работы бота"""

    if os.path.exists(".env"):
        load_dotenv()

    type_db = os.getenv("TYPE_DB")

    if type_db == "mysql":
        return Config(
            tg_bot=TgBot(token=os.getenv("BOT_TOKEN")),
            data_base=DataBase(
                host=os.getenv("HOST_DB"),
                port=int(os.getenv("PORT_DB")),
                user=os.getenv("USER_DB"),
                password=os.getenv("PASSWORD_DB"),
                name_db=os.getenv("NAME_DB"),
            ),
            type_db=type_db,
            redis=Redis(
                host=os.getenv("REDIS_HOST"),
                port=int(os.getenv("REDIS_PORT")),
                password=os.getenv("REDIS_PASSWORD"),
            ),
        )
    elif type_db == "sqlite":
        return Config(
            tg_bot=TgBot(token=os.getenv("BOT_TOKEN")),
            type_db=type_db,
        )


config: Config = load_config()
