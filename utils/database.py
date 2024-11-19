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

    async def query(self, query: str) -> Tuple[Any]:
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                try:
                    await cursor.execute(query)
                    response = await cursor.fetchall()
                    return response

                except aiomysql.OperationalError as e:
                    if e.args[0] == 2013:  # Lost connection to SQL server during query
                        await self.auth(self.__authUser, self.__authPassword, self.__authDatabase, self.__authAutocommit)
                        return await self.query(query)
                    raise e

                except Exception as e:
                    raise e
                
    
    async def close(self) -> None:
        self.pool.close()
        await self.pool.wait_closed()
