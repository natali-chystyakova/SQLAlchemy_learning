from sqlalchemy import insert, select, func, cast, Integer, and_
from src.database import sync_engine, async_engine, session_factory, async_session_factory, Base
from src.models import WorkersOrm, ResumesOrm, Workload, VacanciesOrm
from sqlalchemy.orm import aliased, joinedload, selectinload, contains_eager

from src.schemas import WorkersRelDTO, WorkloadAvgCompensationDTO, ResumesRelVacanciesRepliedDTO


# def create_tables():
#
#     #metadata_obj.drop_all(sync_engine)
#     Base.metadata.drop_all(sync_engine)
#     sync_engine.echo = True
#     #metadata_obj.create_all(sync_engine)
#     Base.metadata.create_all(sync_engine)
#
#     sync_engine.echo = True
#
#
#
# def insert_data():
#     with session_factory() as session:
#         worker_jack = WorkersOrm(username="Jack")
#         worker_michael = WorkersOrm(username="Michael")
#         # session.add(worker_michael)
#         # session.add(worker_jack)
#         session.add_all([worker_jack, worker_michael]) # если много обьектов
#         session.commit()


class SyncORM:
    @staticmethod
    def create_tables():
        sync_engine.echo = False
        Base.metadata.drop_all(sync_engine)
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with session_factory() as session:
            worker_jack = WorkersOrm(username="Jack")
            worker_michael = WorkersOrm(username="Michael")
            session.add_all([worker_jack, worker_michael])
            # flush отправляет запрос в базу данных
            # После flush каждый из работников получает первичный ключ id, который отдала БД
            session.flush()  # отправляем изменения в базу , без завершения запроса
            session.commit()  # завершаем запрос

    @staticmethod
    def insert_resumes():
        with session_factory() as session:
            resume_jack_1 = ResumesOrm(
                title="Python Junior Developer", compensation=50000, workload=Workload.fulltime, worker_id=1
            )
            resume_jack_2 = ResumesOrm(
                title="Python Data", compensation=250000, workload=Workload.fulltime, worker_id=1
            )
            resume_michael_1 = ResumesOrm(
                title="Python Scientist", compensation=300000, workload=Workload.parttime, worker_id=2
            )

            session.add_all([resume_jack_1, resume_jack_2, resume_michael_1])
            # flush отправляет запрос в базу данных
            # После flush каждый из работников получает первичный ключ id, который отдала БД
            session.flush()  # отправляем изменения в базу , без завершения запроса
            session.commit()  # завершаем запрос

    @staticmethod
    def select_resumes_avg_compensation(like_language: str = "Python"):
        """
        select workload, avg(compensation)::int as avg_compensation
        from resumes
        where title like '%Python%' and compensation > 40000
        group by workload
        having avg(compensation) > 70000
        """
        with session_factory() as session:
            query = (
                select(
                    ResumesOrm.workload,
                    cast(func.avg(ResumesOrm.compensation), Integer).label("avg_compensation"),
                )
                .select_from(ResumesOrm)
                .filter(
                    and_(
                        ResumesOrm.title.contains(like_language),
                        ResumesOrm.compensation > 40000,
                    )
                )
                .group_by(ResumesOrm.workload)
                .having(func.avg(ResumesOrm.compensation) > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = session.execute(query)
            result = res.all()
            print(result)
            print(result[0].avg_compensation)

    @staticmethod
    def select_workers():
        with session_factory() as session:
            # worker_id=1
            # worker_jack= session.get(WorkersOrm, worker_id) # если мы хотим получить одного работника
            query = select(WorkersOrm)  # SELECT * FROM workers
            result = session.execute(query)
            workers = result.scalars().all()  # вфвксти все значения итератора result
            print(f"{workers=}")

    @staticmethod
    def update_workers(worker_id: int = 1, new_username: str = "Vania"):
        with session_factory() as session:
            worker_jack = session.get(WorkersOrm, worker_id)  # получаем обьект
            worker_jack.username = new_username  # меняем имя
            session.expire()  # сброс именения
            # session.refresh() # забирает последнее обновление из базы данных.
            session.commit()

    @staticmethod
    def insert_additional_resumes():
        with session_factory() as session:
            workers = [
                {"username": "Artem"},  # id 3
                {"username": "Roman"},  # id 4
                {"username": "Petr"},  # id 5
            ]
            resumes = [
                {"title": "Python программист", "compensation": 60000, "workload": "fulltime", "worker_id": 3},
                {"title": "Machine Learning Engineer", "compensation": 70000, "workload": "parttime", "worker_id": 3},
                {"title": "Python Data Scientist", "compensation": 80000, "workload": "parttime", "worker_id": 4},
                {"title": "Python Analyst", "compensation": 90000, "workload": "fulltime", "worker_id": 4},
                {"title": "Python Junior Developer", "compensation": 100000, "workload": "fulltime", "worker_id": 5},
            ]
            insert_workers = insert(WorkersOrm).values(workers)
            insert_resumes = insert(ResumesOrm).values(resumes)
            session.execute(insert_workers)
            session.execute(insert_resumes)
            session.commit()

    @staticmethod
    def select_workers_with_lazy_relationship():  # ленивая подгрузка
        with session_factory() as session:
            query = select(WorkersOrm)
            res = session.execute(query)
            result = res.scalars().all()  # список работников
            worker_1_resumes = result[0].resumes  # все резюме первого работника
            print(worker_1_resumes)
            worker_2_resumes = result[1].resumes  # все резюме второго работника
            print(worker_2_resumes)

    @staticmethod
    def select_workers_with_joined_relationship():  # для MANY_TO_ONE и ONE_TO_ONE
        with session_factory() as session:
            query = select(WorkersOrm).options(
                joinedload(WorkersOrm.resumes)
            )  # одноврменно с вборкой работников, присоединять к ним и  резюме
            res = session.execute(query)
            result = res.unique().scalars().all()  # список работников unique() - для уникальности перв.ключей
            worker_1_resumes = result[0].resumes  # все резюме первого работника
            print(worker_1_resumes)
            worker_2_resumes = result[1].resumes  # все резюме второго работника
            print(worker_2_resumes)

    @staticmethod
    def select_workers_with_selectin_relationship():  # подходит для ONE_TO_MANY и MANY_TO_MANY
        with session_factory() as session:
            query = (
                select(WorkersOrm).options(selectinload(WorkersOrm.resumes))
                # одноврменно с вборкой работников, присоединять к ним и  резюме
            )
            res = session.execute(query)
            result = res.unique().scalars().all()  # список работников unique() - для уникальности перв.ключей
            worker_1_resumes = result[0].resumes  # все резюме первого работника
            print(worker_1_resumes)
            worker_2_resumes = result[1].resumes  # все резюме второго работника
            print(worker_2_resumes)

    @staticmethod
    def select_workers_with_condition_relationship():
        with session_factory() as session:
            query = (
                select(WorkersOrm).options(selectinload(WorkersOrm.resumes_parttime))
                # одноврменно с вборкой работников, присоединять к ним и  резюме по условию только с парттайм
            )
            res = session.execute(query)
            result = res.scalars().all()
            print(result)

    #
    @staticmethod
    def select_workers_with_condition_relationship_contains_eager():
        with session_factory() as session:
            query = (
                select(WorkersOrm)
                .join(WorkersOrm.resumes)  # соединяем сами без вложенности
                .options(contains_eager(WorkersOrm.resumes))  # делаемвложенность
                .filter(ResumesOrm.workload == "parttime")  # фильтр по workload
            )
            res = session.execute(query)
            result = res.unique().scalars().all()
            print(result)

    @staticmethod
    def select_workers_with_condition_relationship_contains_eager_with_limit():
        with session_factory() as session:
            subq = (
                select(ResumesOrm.id.label("parttime_resume_id"))
                .filter(ResumesOrm.worker_id == WorkersOrm.id)
                .order_by(WorkersOrm.id.desc())
                .limit(2)
                .scalar_subquery()
                .correlate(WorkersOrm)
            )
            query = (
                select(WorkersOrm).join(ResumesOrm, ResumesOrm.id.in_(subq)).options(contains_eager(WorkersOrm.resumes))
            )
            res = session.execute(query)
            result = res.unique().scalars().all()
            print(result)

    @staticmethod
    def convert_workers_to_dto():
        with session_factory() as session:
            query = select(WorkersOrm).options(selectinload(WorkersOrm.resumes)).limit(2)
            res = session.execute(query)
            result_orm = res.scalars().all()
            print(f"{result_orm}")
            result_dto = [WorkersRelDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"{result_dto=}")
            return result_dto

    @staticmethod
    def convert_select_resumes_avg_compensation_to_dto(like_language: str = "Python"):

        with session_factory() as session:
            query = (
                select(
                    ResumesOrm.workload,
                    cast(func.avg(ResumesOrm.compensation), Integer).label("avg_compensation"),
                )
                .select_from(ResumesOrm)
                .filter(
                    and_(
                        ResumesOrm.title.contains(like_language),
                        ResumesOrm.compensation > 40000,
                    )
                )
                .group_by(ResumesOrm.workload)
                .having(func.avg(ResumesOrm.compensation) > 70000)
            )

            res = session.execute(query)
            result_orm = res.all()
            print(f"{result_orm=}")
            result_dto = [WorkloadAvgCompensationDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"{result_dto=}")
            return result_dto

    @staticmethod
    def add_vacancies_and_replies():
        with session_factory() as session:
            new_vacancy = VacanciesOrm(title="Python разработчик", compensation=100000)
            resume_1 = session.get(ResumesOrm, 1)
            resume_2 = session.get(ResumesOrm, 2)
            resume_1.vacancies_replied.append(new_vacancy)
            resume_2.vacancies_replied.append(new_vacancy)
            session.commit()

    @staticmethod
    def select_resumes_with_all_relationships():
        with session_factory() as session:
            query = (
                select(ResumesOrm)
                .options(joinedload(ResumesOrm.worker))  # связь много к одному
                .options(
                    selectinload(ResumesOrm.vacancies_replied).load_only(VacanciesOrm.title)
                )  # связь многие ко многим
            )
            res = session.execute(query)
            result_orm = res.unique().scalars().all()
            print(f"{result_orm=}")
            result_dto = [ResumesRelVacanciesRepliedDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"{result_dto=}")
            return result_dto


# асинхронный запрос на вставку данных
# async def insert_data():
#     async with async_session_factory() as session:
#         worker_jack = WorkersOrm(username="Jack")
#         worker_michael = WorkersOrm(username="Michael")
#         # session.add(worker_michael)
#         # session.add(worker_jack)
#         session.add_all([worker_jack, worker_michael]) # ничего не отправляет в базу, не надo await
#         await session.commit()


class AsyncORM:
    # Асинхронный вариант, не показанный в видео
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def insert_workers():
        async with async_session_factory() as session:
            worker_jack = WorkersOrm(username="Jack")
            worker_michael = WorkersOrm(username="Michael")
            session.add_all([worker_jack, worker_michael])
            # flush взаимодействует с БД, поэтому пишем await
            await session.flush()
            await session.commit()

    @staticmethod
    async def join_cte_subquery_window_func(like_language: str = "Python"):
        """
        # na=# WITH helper_2 AS(
        # na(# SELECT *, (helper_1.compensation - helper_1.avg_workload_comp) AS comp_diff
        # na(# FROM (
        # na(# SELECT
        # na(# w.id,
        # na(# w.username,
        # na(# r.compensation,
        # na(# r.workload,
        # na(# avg(r.compensation) OVER(PARTITION BY r.workload)::int AS avg_workload_comp
        # na(# FROM resumes r
        # na(# JOIN workers w ON r.worker_id = w.id
        # na(# ) helper_1
        # na(# )
        # na-# SELECT * FROM helper_2
        # na-# ORDER BY comp_diff DESC
        """
        async with async_session_factory() as session:
            r = aliased(ResumesOrm)
            w = aliased(WorkersOrm)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.compensation).over(partition_by=r.workload).cast(Integer).label("avg_workload_comp"),
                )
                .select_from(r)
                .join(w, r.worker_id == w.id)
                .subquery("helper_1")
            )
            cte = select(
                subq.c.worker_id,
                subq.c.username,
                subq.c.compensation,
                subq.c.workload,
                subq.c.avg_workload_comp,
                (subq.c.compensation - subq.c.avg_workload_comp).label("comp_diff"),
            ).cte("helper_2")
            query = select(cte).order_by(cte.c.comp_diff.desc())
            # print(query.compile(compile_kwargs={"literal_binds": True}))
            res = await session.execute(query)
            result = res.all()
            print(result)
            print(f"{len(result)=}. {result=}")


# вход в мою базу данных  psql -h localhost -p 5432 -U postgres -d na

# na=# SELECT *, (helper_1.compensation - helper_1.avg_workload_comp) AS comp_diff
# na-# FROM (
# na(# SELECT
# na(# w.id,
# na(# w.username,
# na(# r.compensation,
# na(# r.workload,
# na(# avg(r.compensation) OVER(PARTITION BY r.workload)::int AS avg_workload_comp
# na(# FROM resumes r
# na(# JOIN workers w ON r.worker_id = w.id
# na(# ) helper_1
# na-# ORDER BY helper_1.compensation - helper_1.avg_workload_comp DESC;


# na=# WITH helper_2 AS(
# na(# SELECT *, (helper_1.compensation - helper_1.avg_workload_comp) AS comp_diff
# na(# FROM (
# na(# SELECT
# na(# w.id,
# na(# w.username,
# na(# r.compensation,
# na(# r.workload,
# na(# avg(r.compensation) OVER(PARTITION BY r.workload)::int AS avg_workload_comp
# na(# FROM resumes r
# na(# JOIN workers w ON r.worker_id = w.id
# na(# ) helper_1
# na(# )
# na-# SELECT * FROM helper_2
# na-# ORDER BY comp_diff DESC
