import asyncio
import aiomysql
from typing import Tuple, Optional, Any


class DataSQL():
    def __init__(self, host: str = "127.0.0.1", port: int = 3306, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self.loop, self.host, self.port = loop, host, port

    async def auth(self, user: str = "root", password: str = "", database: str = "mysql", autocommit: bool = True) -> None:
        self.__authUser, self.__authPassword, self.__authDatabase, self.__authAutocommit = user, password, database, autocommit
        self.pool: aiomysql.pool.Pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=user,
            password=password,
            db=database,
            loop=self.loop,
            autocommit=autocommit
        )

    async def execute(self, query: str, args = None) -> Tuple[Any]:
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                try:
                    await cursor.execute(query, args)
                    response = await cursor.fetchall()
                    return response
                except aiomysql.OperationalError as e:
                    if e.args[0] == 2013:  # Lost connection to SQL server during query
                        await self.auth(self.__authUser, self.__authPassword, self.__authDatabase, self.__authAutocommit)
                        return await self.execute(query, args)
                    raise e
                except Exception as e:
                    raise e
    

    async def execute_fetchone(self, query: str, args = None):
        result = await self.execute(query, args)
        if any(result):
            return result[0]
        
        return None


    
    async def execute_insert(self, query: str, args = None):
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                try:
                    await cursor.execute(query, args)
                    return cursor.lastrowid
                except aiomysql.OperationalError as e:
                    if e.args[0] == 2013:  # Lost connection to SQL server during query
                        await self.auth(self.__authUser, self.__authPassword, self.__authDatabase, self.__authAutocommit)
                        return await self.execute_insert(query, args)
                    raise e
                except Exception as e:
                    raise e

    
    async def close(self) -> None:
        self.pool.close()
        await self.pool.wait_closed()
