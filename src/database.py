from typing import Annotated

from sqlalchemy import String, create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import settings

sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True,
    # pool_size=5,
    # max_overflow=10,
)
# создание асинхронного движка
async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True,
    # pool_size=5,
    # max_overflow=10,
)

session_factory = sessionmaker(sync_engine)
async_session_factory = async_sessionmaker(async_engine)


str_200 = Annotated[str, 200]


class Base(DeclarativeBase):
    type_annotation_map = {str_200: String(200)}
    # def __repr__(self):
    #     cols = []
    #     for col in self.__table__.columns.keys():
    #         cols.append(f'{col}={getattr(self, col)}')
    #     return f'<{self.__class__.__name__}{",".join(cols)}>'
    # доработанный репр
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"

    # вход в мою базу данных  psql -h localhost -p 5432 -U postgres -d na
