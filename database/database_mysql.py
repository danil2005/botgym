from datetime import datetime
from config_data.config import DataBase as DataBase_config
import aiomysql
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from asyncio import sleep
from database.database_abstract import AbstractDataBase

class DataBaseMySQL(AbstractDataBase):

    def __init__ (self, config: DataBase_config):
        self.host = config.host
        self.port = config.port
        self.user = config.user
        self.password = config.password
        self.name_db = config.name_db

    @asynccontextmanager
    async def get_db_cursor(self) -> AsyncGenerator[aiomysql.Cursor, None]:
        """Контекстный менеджер, который возвращает курсор.
        Автоматически закрыввает подключение и курсор при выходе из менеджера"""
        conn = await aiomysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.name_db
        )
        cursor = await conn.cursor()
        try:
            yield cursor
        finally:
            await cursor.close()
            conn.close()

    async def check_db(self) -> None:
        """Проверяет БД. При необходимости создает новую БД со структурой"""
        config_db = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password
        }

        for i in range(5):
            try:
                conn = await aiomysql.connect(**config_db)
            except:
                await sleep(5)
        conn = await aiomysql.connect(**config_db)

        check_db_query = f"SHOW DATABASES LIKE '{self.name_db}'"
        create_db_query = f"CREATE DATABASE {self.name_db}"
        
        async with conn.cursor() as cursor:
            await cursor.execute(check_db_query)
            result = await cursor.fetchone()
            if not result:
                await cursor.execute(create_db_query)
            else:
                return
        
        await conn.select_db(self.name_db)
        with open('create_tables_mysql.sql', 'r', encoding='utf-8') as file:
            sql_script = file.read()
        sql_commands = sql_script.split(';')
        
        async with conn.cursor() as cursor:
            for command in sql_commands:
                if command.strip():
                    await cursor.execute(command)
        await conn.commit()
        conn.close()

    async def add_questionnaire(self, data: dict)  -> None:
        """Добавляет анкету пользователя в БД"""
        query = '''
            INSERT INTO Users
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, tuple(data.values()))
            await cursor.connection.commit()

    async def check_name_workout_type(self, user_id: int, name: str) -> bool:
        """Проверяет есть ли уже такое имя типа тренировки в БД"""
        query = '''
            SELECT * FROM Workout_types
            WHERE user_id = %s AND name = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (user_id, name))
            rows = await cursor.fetchall()
        return bool(rows)

    async def add_new_workout_type(self, user_id: int, name: str) -> None:
        """Создает новый тип тренировки"""
        if await self.check_name_workout_type(user_id, name):
            return False
        query = '''
            INSERT INTO Workout_types (user_id, name, is_active)
            VALUES (%s, %s, %s)
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (user_id, name, True))
            await cursor.connection.commit()
        return True

    async def get_workout_types(self, user_id: int, is_active = None) -> list[tuple]:
        """Возвращает типы тренировок пользователя - активные, неактивные, все"""
        query = '''
            SELECT id, name FROM Workout_types
            WHERE user_id = %s
        '''
        query_is_active = 'AND is_active = %s'

        async with self.get_db_cursor() as cursor:
            if is_active == 'active':
                await cursor.execute(query + query_is_active, (user_id, 1))
            elif is_active == 'deactive':
                await cursor.execute(query + query_is_active, (user_id, 0))
            else:
                await cursor.execute(query, (user_id,))
            rows = await cursor.fetchall()
        return rows

    async def set_active_workout_type(self, workout_type: int, is_active: bool) -> None:
        """Устанавливает флаг активности типа тренировки"""
        query = '''
            UPDATE Workout_types SET is_active = %s
            WHERE id = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (is_active, workout_type))
            await cursor.connection.commit()

    async def delete_workout_type(self, workout_type: int) -> None:
        """Удаляет тип тренировки"""
        query = '''
            DELETE FROM Workout_types
            WHERE id = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (workout_type,))
            await cursor.connection.commit()

    async def get_name_workout_type(self, workout_type: int) -> str:
        """Возвращает имя типа тренировки"""
        query = '''
            SELECT name FROM Workout_types
            WHERE id = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (workout_type,))
            row = await cursor.fetchone()
        return row[0]

    async def check_name_exercise_type(self, user_id: int, name: str) -> bool:
        """Проверяет есть ли упражнение с таким именем у пользователя"""
        query = '''
            SELECT * FROM Exercise_types
            WHERE user_id = %s AND name = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (user_id, name))
            rows = await cursor.fetchall()
        return bool(rows)

    async def add_new_exercise_type(self, user_id: int, name: str) -> int:
        """Создает новый тип упражнения"""
        if await self.check_name_exercise_type(user_id, name):
            return False
        query = '''
            INSERT INTO Exercise_types (user_id, name)
            VALUES (%s, %s)
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (user_id, name))
            last_id = cursor.lastrowid
            await cursor.connection.commit()
        return last_id

    async def start_workout(self, user_id: int, workout_type: int) -> int:
        """Фиксирует в БД страт тренировки"""
        date = datetime.today().strftime("%Y-%m-%d")
        start = datetime.now().strftime("%H:%M:%S")
        query = '''
            INSERT INTO Workouts (user_id, type_id, date, start)
            VALUES (%s, %s, %s, %s)
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (user_id, workout_type, date, start))
            last_id = cursor.lastrowid
            await cursor.connection.commit()
        return last_id

    async def start_exercise(self, exercise_type: int, workout: int) -> int:
        """Записывает в БД старт упражнения"""
        query = '''
            INSERT INTO Exercises (type_id, id_workout, weight)
            VALUES (%s, %s, "")
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (exercise_type, workout))
            last_id = cursor.lastrowid
            await cursor.connection.commit()
        return last_id

    async def get_weight_workout(self, workout: int) -> list[tuple]:
        """Возвращает выполненые упражнения с весами для конкретной тренировки"""
        query = '''
            SELECT Exercise_types.name, Exercises.weight, Exercises.id
            FROM Exercises
            INNER JOIN Exercise_types ON Exercises.type_id = Exercise_types.id
            WHERE Exercises.id_workout = %s
            ORDER BY Exercises.id ASC
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (workout,))
            rows = await cursor.fetchall()
        return rows

    async def end_workout(self, workout: int) -> None:
        """Фиксирует в БД конец тренировки"""
        query_get_workout = '''
            SELECT date, start FROM Workouts
            WHERE id = %s
        '''
        query_update_workout = '''
            UPDATE Workouts SET end = %s, duration = %s
            WHERE id = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query_get_workout, (workout,))
            rows = await cursor.fetchall()
        start = datetime.combine(rows[0][0], datetime.min.time()) + rows[0][1]
        end = datetime.now()
        duration = (end - start).total_seconds() // 60
        end_str = end.strftime("%H:%M:%S")
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query_update_workout, (end_str, duration, workout))
            await cursor.connection.commit()

    async def get_workout_exercises(self, workout_type: int) -> list[tuple]:
        """Возвращает типы упражнения, которые были в последней тренировке этого типа"""
        query_get_latest_workout = '''
            SELECT id
            FROM Workouts
            WHERE type_id = %s AND end IS NOT NULL
            ORDER BY id DESC
            LIMIT 1
        '''
        query_get_exercises = '''
            SELECT Exercises.type_id, Exercise_types.name
            FROM Exercises
            INNER JOIN Exercise_types ON Exercises.type_id = Exercise_types.id
            WHERE Exercises.id_workout = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query_get_latest_workout, (workout_type,))
            row = await cursor.fetchone()
        if not row:
            return []
        id_workout = row[0]
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query_get_exercises, (id_workout,))
            rows = await cursor.fetchall()
        return rows

    async def get_latest_workout_ids(self, workout_type: int) -> list[int]:
        """Возвращает последние 3 id тренировок для типа тренировки"""
        query = '''
            SELECT id
            FROM Workouts
            WHERE type_id = %s
            ORDER BY id DESC
            LIMIT 3
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (workout_type,))
            rows = await cursor.fetchall()
        return [row[0] for row in rows]

    async def get_date_workout(self, workout: int) -> str:
        """Возвращает дату тренировки"""
        query = '''
            SELECT date FROM Workouts
            WHERE id = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (workout,))
            rows = await cursor.fetchall()
        return rows[0][0].strftime("%d-%m-%Y")

    async def update_exercise(self, exercise: int, weight: str) -> None:
        """Добавляет новый вес к упражнению"""
        query_get_weight = '''
            SELECT weight FROM Exercises
            WHERE id = %s
        '''
        query_update_weight = '''
            UPDATE Exercises SET weight = %s
            WHERE id = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query_get_weight, (exercise,))
            row = await cursor.fetchone()
        old_weight = row[0].split(' | ') if row[0] else []
        old_weight.append(weight)
        text_weight = ' | '.join(old_weight)
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query_update_weight, (text_weight, exercise))
            await cursor.connection.commit()

    async def get_all_exercise_types(self, chat_id: int) -> list[tuple]:
        """Возвращает все типы упражнений"""
        query = '''
            SELECT Exercise_types.id, Exercise_types.name
            FROM Exercise_types
            WHERE Exercise_types.user_id = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (chat_id,))
            rows = await cursor.fetchall()
        return rows

    async def get_info_workout(self, workout: int) -> tuple:
        """Возвращает информацию о тренировке"""
        query = '''
            SELECT date, start, duration, type_id FROM Workouts
            WHERE id = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (workout,))
            row = await cursor.fetchone()
        return row

    async def get_exercise_history(self, exercise_type: int) -> list[tuple]:
        """Возвращает веса последних 5 упражнений определенного типа"""
        query = '''
            SELECT Workout_types.name, Workouts.date, Workouts.start, Exercises.weight
            FROM Exercises
            JOIN Workouts ON Exercises.id_workout = Workouts.id
            JOIN Workout_types ON Workouts.type_id = Workout_types.id
            WHERE Exercises.type_id = %s
            LIMIT 5
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (exercise_type,))
            rows = await cursor.fetchall()
        return rows

    async def delete_exercise(self, exercise: int) -> tuple:
        """Удаляет упражнение из тренировки"""
        exercise_del = await self.get_exercise_type(exercise)
        query = '''
            DELETE FROM Exercises
            WHERE id = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (exercise,))
            await cursor.connection.commit()
        return exercise_del

    async def get_exercise_type(self, exercise: int) -> tuple:
        """Возвращает тип упражения"""
        query = '''
            SELECT Exercises.type_id
            FROM Exercises
            INNER JOIN Exercise_types ON Exercises.type_id = Exercise_types.id
            WHERE Exercises.id = %s
        '''
        async with self.get_db_cursor() as cursor:
            await cursor.execute(query, (exercise,))
            row = await cursor.fetchone()
        return row[0]