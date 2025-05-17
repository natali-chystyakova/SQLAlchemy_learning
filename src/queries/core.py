from sqlalchemy import text, insert, select, update
from src.database import sync_engine, async_engine
from src.models import metadata_obj, workers_table


def get_123_sync():
    with sync_engine.connect() as conn:
        # res = conn.execute(text("SELECT VERSION()"))
        res = conn.execute(text("SELECT 1, 2, 3 union select 4, 5, 6"))
        print(f"{res.first()=}")
        conn.commit()


async def get_123_async():
    async with async_engine.connect() as conn:
        res = await conn.execute(text("SELECT 1, 2, 3 union select 4, 5, 6"))
        print(f"{res.first()=}")


# asyncio.run(get_123_async())

# def create_tables():
#     sync_engine.echo=False
#     metadata_obj.drop_all(sync_engine)
#     metadata_obj.create_all(sync_engine)
#     sync_engine.echo = True
#
#
#
# def insert_data():
#     with sync_engine.connect() as conn:
#         # stmt='''INSERT INTO workers (username) VALUES
#         #     ('Jack'),
#         #     ('Michael');'''
#         stmt=insert(workers_table).values(
#             [
#                 {"username": "Jack"},
#                 {"username": "Michael"},
#             ]
#         )
#         # conn.execute(text(stmt))
#         conn.execute(stmt) # такие запросы не оболачиваем в текст
#         conn.commit()


class SyncCore:
    @staticmethod
    def create_tables():
        sync_engine.echo = False
        metadata_obj.drop_all(sync_engine)
        metadata_obj.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with sync_engine.connect() as conn:
            # stmt = """INSERT INTO workers (username) VALUES
            #     ('Jack'),
            #     ('Michael');"""
            stmt = insert(workers_table).values(
                [
                    {"username": "Jack"},
                    {"username": "Michael"},
                ]
            )
            conn.execute(stmt)
            conn.commit()

    @staticmethod
    def select_workers():
        with sync_engine.connect() as conn:
            query = select(workers_table)  # SELECT * FROM workers
            result = conn.execute(query)
            workers = result.all()  # вфвксти все значения итератора result
            print(f"{workers=}")

    @staticmethod
    def update_workers(worker_id: int = 1, new_username: str = "Vania"):
        with sync_engine.connect() as conn:
            # stmt= text("UPDATE workers SET username=:new_username WHERE id=:id")
            # stmt = stmt.bindparams(new_username=new_username, id=worker_id)
            stmt = (
                update(workers_table).values(username=new_username)
                # .where(workers_table.c.id==worker_id)
                .filter_by(id=worker_id)  # то же, что и верхняя строkа
            )

            conn.execute(stmt)
            conn.commit()


class AsyncCore:
    # Асинхронный вариант, не показанный в видео
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(metadata_obj.drop_all)
            await conn.run_sync(metadata_obj.create_all)
