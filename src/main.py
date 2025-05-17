import os
import asyncio  # noqa
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


sys.path.insert(1, os.path.join(sys.path[0], ".."))

# from src.queries.core import create_tables, insert_data
# from src.queries.orm import create_tables, insert_data

from src.queries.core import SyncCore, AsyncCore  # noqa
from src.queries.orm import SyncORM, AsyncORM  # noqa


# create_tables()
# # insert_data()
# asyncio.run(insert_data())

# SyncORM.create_tables()
SyncCore.create_tables()

# SyncORM.insert_workers()
SyncCore.insert_workers()

SyncORM.insert_resumes()  # вставка резюме с ORM
SyncORM.insert_additional_resumes()
# SyncORM.select_workers_with_lazy_relationship() # ленивая загрузка резюме о работников (N+1)
# SyncORM.select_workers_with_joined_relationship() # загрузка всего одним запросом
# SyncORM.select_workers_with_selectin_relationship() # делает 2 запроса: работники и резюме
# SyncORM.select_workers_with_condition_relationship() # делаем запрос по условию
# SyncORM.select_workers_with_condition_relationship_contains_eager()
# SyncORM.select_workers_with_condition_relationship_contains_eager_with_limit()  #ограниченное значение по резюме
SyncORM.convert_workers_to_dto()  # преобразование в пайдентик модель и алхимии (на пути к фастапи)
SyncORM.convert_select_resumes_avg_compensation_to_dto()
SyncORM.add_vacancies_and_replies()
SyncORM.select_resumes_with_all_relationships()

# SyncCore.select_workers()
#
# SyncCore.update_workers()

# SyncORM.select_workers()

# SyncORM.update_workers()
# SyncORM.select_resumes_avg_compensation()


# async def main():
#     await AsyncORM.join_cte_subquery_window_func()
#
# if __name__ == "__main__":
#     asyncio.run(main())


def create_fastapi_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
    )

    @app.get("/workers")
    async def get_workers():
        workers = SyncORM.convert_workers_to_dto()
        return workers

    @app.get("/avg_compensation")
    async def get_avg_compensation():
        compensation = SyncORM.convert_select_resumes_avg_compensation_to_dto()
        return compensation

    @app.get("/resumes")
    async def get_resumes():
        resumes = SyncORM.select_resumes_with_all_relationships()
        return resumes

    return app


app = create_fastapi_app()

if __name__ == "__main__":
    # asyncio.run(main())
    uvicorn.run(
        app="src.main:app",
        reload=True,
    )
