import aiosqlite
import os
from datetime import datetime
from database.database_abstract import AbstractDataBase

class DataBaseSQLite(AbstractDataBase):

    def __init__ (self):
        self.name_file_db = "database.db"

    async def check_db(self, ) -> None:
        """Проверяет БД. При необходимости создает новую БД со структурой"""
        if not os.path.exists(self.name_file_db):
            # Если файл не существует, создаем новую базу данных
            open(self.name_file_db, 'w').close()
        else:
            return
        async with aiosqlite.connect(self.name_file_db) as conn:
            with open('create_tables_sqlite.sql', 'r', encoding='utf-8') as file:
                sql_script = file.read()
            sql_commands = sql_script.split(';')
            cursor = await conn.cursor()
            for command in sql_commands:
                if command.strip():
                    await cursor.execute(command)
            await conn.commit()

    async def add_questionnaire(self, data: dict) -> None:
        """Добавляет анкету пользователя в БД"""
        query = '''
            INSERT INTO Users
            VALUES (?,?,?,?,?,?)
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, tuple(data.values()))
            await conn.commit()

    async def check_name_workout_type(self, user_id: int, name: str) -> bool:
        """Проверяет есть ли уже такое имя тренировки в БД"""
        query = '''
            SELECT * FROM Workout_types
            WHERE user_id = ? AND name = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (user_id, name))
            rows = await cursor.fetchall()
        return bool(rows)

    async def add_new_workout_type(self, user_id: int, name: str) -> None:
        """Создает новый тип тренировки"""
        if await self.check_name_workout_type(user_id, name):
            return False
        query = '''
            INSERT INTO Workout_types (user_id, name, is_active)
            VALUES (?,?,?)
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (user_id, name, True))
            await conn.commit()
        return True

    async def get_workout_types(self, user_id: int, is_active = None) -> list[tuple]:
        """Возвращает типы тренировок пользователя - активные, неактивные, все"""
        query = '''
            SELECT id, name FROM Workout_types
            WHERE user_id = ?
        '''
        query_is_active = 'AND is_active = ?'

        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            if is_active == 'active':
                await cursor.execute(query + query_is_active, (user_id, 1))
            elif is_active == 'deactive':
                await cursor.execute(query + query_is_active, (user_id, 0))
            else:
                await cursor.execute(query, (user_id,))
            rows = await cursor.fetchall()
        return rows

    async def set_active_workout_type(self, workout_type: int, is_active: bool)-> None:
        """Устанавливает флаг активности типа тренировки"""
        query = '''
            UPDATE Workout_types SET is_active = ?
            WHERE id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (is_active, workout_type))
            await conn.commit()

    async def delete_workout_type(self, workout_type: int) -> None:
        """Удаляет тип тренировки"""
        query = '''
            DELETE FROM Workout_types
            WHERE id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (workout_type,))
            await conn.commit()

    async def get_name_workout_type(self, workout_type: int) -> str:
        """Возвращает имя типа тренировки"""
        query = '''
            SELECT name FROM Workout_types
            WHERE id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (workout_type,))
            row = await cursor.fetchone()
        return row[0]

    async def check_name_exercise_type(self, user_id: int, name: str) -> bool:
        """Проверяет есть ли упражнение с таким именем у пользователя"""
        query = '''
            SELECT * FROM Exercise_types
            WHERE user_id = ? AND name = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (user_id, name))
            rows = await cursor.fetchall()
        return bool(rows)

    async def add_new_exercise_type(self, user_id: int, name: str) -> int:
        """Создает новый тип упражнения"""
        if await self.check_name_exercise_type(user_id, name):
            return False
        query = '''
            INSERT INTO Exercise_types (user_id, name)
            VALUES (?,?)
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (user_id, name))
            last_id = cursor.lastrowid
            await conn.commit()
        return last_id

    async def start_workout(self, user_id: int, workout_type: int) -> int:
        """Фиксирует в БД страт тренировки"""
        data = datetime.today().strftime("%d-%m-%Y")
        start = datetime.now().strftime("%H:%M:%S")
        query = '''
            INSERT INTO Workouts (user_id, type_id, data, start)
            VALUES (?,?,?,?)
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (user_id, workout_type, data, start))
            last_id = cursor.lastrowid
            await conn.commit()
        return last_id

    async def start_exercise(self, exercise_type: int, workout: int) -> int:
        """Записывает в БД старт упражнения"""
        query = '''
            INSERT INTO Exercises (type_id, id_workout, weight)
            VALUES (?,?,"")
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (exercise_type, workout))
            last_id = cursor.lastrowid
            await conn.commit()
        return last_id

    async def get_weight_workout(self, workout: int) -> list[tuple]:
        """Возвращает выполненые упражнения с весами для конкретной тренировки"""
        query = '''
            SELECT Exercise_types.name, Exercises.weight, Exercises.id
            FROM Exercises
            INNER JOIN Exercise_types ON Exercises.type_id = Exercise_types.id
            WHERE Exercises.id_workout = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (workout,))
            rows = await cursor.fetchall()
        return rows

    async def end_workout(self, workout: int) -> None:
        """Фиксирует в БД конец тренировки"""
        query_select = '''
            SELECT data, start FROM Workouts
            WHERE id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query_select, (workout,))
            rows = await cursor.fetchall()
        date_start = datetime.strptime(rows[0][0], "%d-%m-%Y").date()
        time_start = datetime.strptime(rows[0][1], "%H:%M:%S").time()
        start = datetime.combine(date_start, time_start)
        end = datetime.now()
        duration = (end - start).total_seconds() // 60
        end_str = end.strftime("%H:%M:%S")

        query_update = '''
            UPDATE Workouts SET end = ?, duration = ?
            WHERE id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query_update, (end_str, duration, workout))
            await conn.commit()

    async def get_workout_exercises(self, workout_type: int) -> list[tuple]:
        """Возвращает типы упражнения, которые были в последней тренировке этого типа"""
        query_last_workout = '''
            SELECT id
            FROM Workouts
            WHERE type_id = ? AND end IS NOT NULL
            ORDER BY id DESC
            LIMIT 1
        '''
        query_exercises = '''
            SELECT Exercises.type_id, Exercise_types.name
            FROM Exercises
            INNER JOIN Exercise_types ON Exercises.type_id = Exercise_types.id
            WHERE Exercises.id_workout = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query_last_workout, (workout_type,))
            row = await cursor.fetchone()

        if not row:
            return []
        id_workout = row[0]
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query_exercises, (id_workout,))
            rows = await cursor.fetchall()

        return rows

    async def get_latest_workout_ids(self, workout_type: int) -> list[int]:
        """Возвращает последние 3 id тренировок для типа тренировки"""
        query = '''
            SELECT id
            FROM Workouts
            WHERE type_id = ?
            ORDER BY id DESC
            LIMIT ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (workout_type, 3))
            rows = await cursor.fetchall()
        return [i[0] for i in rows]

    async def get_date_workout(self, workout: int) -> str:
        """Возвращает дату тренировки"""
        query = '''
            SELECT data FROM Workouts
            WHERE id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (workout,))
            rows = await cursor.fetchall()
        return rows[0][0]

    async def update_exercise(self, exercise: int, weight: str) -> None:
        """Добавляет новый вес к упражнению"""
        query_select = '''
            SELECT weight FROM Exercises
            WHERE id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query_select, (exercise,))
            row = await cursor.fetchone()
        if not row[0]:
            old_weight = []
        else:
            old_weight = row[0].split(' | ')
        old_weight.append(weight)
        text_weight = ' | '.join(old_weight)

        query_update = '''
            UPDATE Exercises SET weight = ?
            WHERE id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query_update, (text_weight, exercise))
            await conn.commit()

    async def get_all_exercise_types(self, chat_id: int) -> list[tuple]:
        """Возвращает все типы упражнений"""
        query = '''
            SELECT Exercise_types.id, Exercise_types.name
            FROM Exercise_types
            WHERE Exercise_types.user_id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (chat_id,))
            rows = await cursor.fetchall()
        return rows

    async def get_info_workout(self, workout: int) -> tuple:
        """Возвращает информацию о тренировке"""
        query = '''
            SELECT data, start, duration, type_id FROM Workouts
            WHERE id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (workout,))
            row = await cursor.fetchone()
        return row


    async def get_exercise_history(self, exercise_type: int) -> list[tuple]:
        """Возвращает веса последних 5 упражнений определенного типа"""
        query = '''
            SELECT Workout_types.name, Workouts.data, Workouts.start, Exercises.weight
            FROM Exercises
            JOIN Workouts ON Exercises.id_workout = Workouts.id
            JOIN Workout_types ON Workouts.type_id = Workout_types.id
            WHERE Exercises.type_id = ?
            LIMIT 5
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (exercise_type,))
            rows = await cursor.fetchall()
        return rows

    async def delete_exercise(self, exercise: int) -> tuple:
        """Удаляет упражнение из тренировки"""
        exerecise_del = await self.get_exercise_type(exercise)
        query = '''
            DELETE FROM Exercises
            WHERE id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (exercise,))
            await conn.commit()
        return exerecise_del

    async def get_exercise_type(self, exercise: int) -> tuple:
        """Возвращает тип упражения"""
        query = '''
            SELECT Exercises.type_id
            FROM Exercises
            INNER JOIN Exercise_types ON Exercises.type_id = Exercise_types.id
            WHERE Exercises.id = ?
        '''
        async with aiosqlite.connect(self.name_file_db) as conn:
            cursor = await conn.cursor()
            await cursor.execute(query, (exercise,))
            row = await cursor.fetchone()
        return row[0]