from dataclasses import dataclass
from environs import Env


@dataclass
class Bot:
    token: str


@dataclass
class DB:
    host: str
    db_name: str
    user: str
    password: str
    port: str


@dataclass
class Config:
    bot: Bot
    db: DB


def load_config(path: str = None):
    # TODO: Add some checks here?
    env = Env()
    env.read_env(path)
    
    return Config(
        bot=Bot(token=env.str("BOT_TOKEN")),
        db=DB(
            host=env.str("DB_HOST"),
            db_name=env.str("DB_NAME"),
            user=env.str("DB_USER"),
            password=env.str("DB_PASS"),
            port=env.str("DB_PORT")
        )
    )
