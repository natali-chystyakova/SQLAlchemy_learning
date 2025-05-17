import datetime

from typing import Annotated

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import text, TIMESTAMP, Enum, CheckConstraint, Index, PrimaryKeyConstraint  # noqa
from src.database import Base, str_200
from sqlalchemy.orm import Mapped, mapped_column, relationship


# import enum
from src.enums import Workload  # перечисления держим в одельном файле


intpk = Annotated[int, mapped_column(primary_key=True)]  # кастомная аннотиция типов

# created_at= Annotated[datetime.datetime,
# mapped_column(server_default=text('TIMEZONE("utc", now())'))]
created_at = Annotated[datetime.datetime, mapped_column(default=datetime.datetime.utcnow())]
# updated_at= Annotated[datetime.datetime,
# mapped_column(server_default=text('TIMEZONE("utc", now())'), onupdate=datetime.datetime.utcnow,)]
updated_at = Annotated[
    datetime.datetime, mapped_column(default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())
]


class WorkersOrm(Base):
    __tablename__ = "workers"  # обьявляем имя таблицы
    # id: Mapped[int]=mapped_column(primary_key=True)
    id: Mapped[intpk]  # вместо предыдущей строки
    # username: Mapped[str]=mapped_column()
    username: Mapped[str]  # можно не указывать
    resumes: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="worker",
        # backref="worker" # создаст связь с резюме само
    )  # связываем работника с резюме(рез. - много, по этому list
    resumes_parttime: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="worker",
        primaryjoin="and_(WorkersOrm.id==ResumesOrm.worker_id, ResumesOrm.workload=='parttime')",
        order_by="ResumesOrm.id.desc()",  # сортировка
        # lazy="selectin" # тип подгрузки, считается не явным
        # с условием по рабочему времени только parttime
    )


# class Workload(enum.Enum):  # перечисления держим в тодельном файле
#     parttime = "parttime"
#     fulltime = "fulltime"


class ResumesOrm(Base):
    __tablename__ = "resumes"
    # id: Mapped[int] = mapped_column(primary_key=True)
    id: Mapped[intpk]
    # title: Mapped[str]=mapped_column(String(200))
    title: Mapped[str_200]  # как предыдущее но с кастомным типом
    # compensation: Mapped[int]=mapped_column(nullable=True)  # поле может иметь значение 0
    # compensation: Mapped[int | None] # поле может иметь значение 0
    compensation: Mapped[int | None]
    # compensation: Mapped[int]

    # workload: Mapped[Workload]
    workload: Mapped[Workload] = mapped_column(Enum(Workload))
    # worker_id: Mapped[int]=mapped_column(ForeignKey(WorkersOrm.id))  #модель.столбец
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id", ondelete="CASCADE"))
    # created_at:Mapped[datetime.datetime]=mapped_column(server_default=text('TIMEZONE("utc", now())'))
    # updated_at: Mapped[datetime.datetime] = mapped_column(server_default=text('TIMEZONE("utc", now())'),
    #                                                       onupdate=datetime.datetime.utcnow,)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    worker: Mapped["WorkersOrm"] = relationship(
        back_populates="resumes",
    )  # укажем, каксвязана таблица резюме с работниками

    # def __repr__(self):
    #     return f"<Resume id={self.id}, title={self.title}>"

    vacancies_replied: Mapped[list["VacanciesOrm"]] = relationship(
        back_populates="resumes_replied",
        secondary="vacancies_replies",
    )

    repr_cols_num = 4
    repr_cols = ("created_at",)
    __table_args__ = (
        # PrimaryKeyConstraint("id",), # если мы хотим задать первичные ключи
        Index("title_index", "title"),
        CheckConstraint("compensation > 0", name="check_compensation_positive"),  # поставить ограничение на значение
    )


class VacanciesOrm(Base):
    __tablename__ = "vacancies"
    id: Mapped[intpk]
    title: Mapped[str_200]
    compensation: Mapped[int | None]
    resumes_replied: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="vacancies_replied",
        secondary="vacancies_replies",
    )


class VacanciesRepliesOrm(Base):  # связь многие-ко-многим
    __tablename__ = "vacancies_replies"
    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id", ondelete="CASCADE"), primary_key=True)
    cover_letter: Mapped[str | None]


metadata_obj = MetaData()

workers_table = Table(
    "workers",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String),
)

resumes_table = Table(
    "resumes",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("title", String(256)),
    Column("compensation", Integer, nullable=True),
    Column("workload", Enum(Workload)),
    Column("worker_id", ForeignKey("workers.id", ondelete="CASCADE")),
    Column("created_at", TIMESTAMP, server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP, server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow),
)

vacancies_table = Table(
    "vacancies",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("compensation", Integer, nullable=True),
)

vacancies_replies_table = Table(
    "vacancies_replies",
    metadata_obj,
    Column("resume_id", ForeignKey("resumes.id", ondelete="CASCADE"), primary_key=True),
    Column("vacancy_id", ForeignKey("vacancies.id", ondelete="CASCADE"), primary_key=True),
)


# alembic init src/migrations создание базы данных миграций
# alembic revision --autogenerate проведение миграций
# alembic upgrade head провести изменения в базу данных
#  alembic downgrade 7cf07797f5c0 откатиться до заданной миграции
#  alembic downgrade base откатиться вообще все
# alembic revision  создать пустую миграцию
