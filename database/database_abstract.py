from abc import ABC, abstractmethod

class AbstractDataBase (ABC):

    @abstractmethod
    async def check_db() -> None:
        """Проверяет БД. При необходимости создает новую БД со структурой"""
        pass

    @abstractmethod
    async def add_questionnaire(data: dict)  -> None:
        """Добавляет анкету пользователя в БД"""
        pass

    @abstractmethod
    async def add_new_workout_type(user_id: int, name: str) -> None:
        """Создает новый тип тренировки"""
        pass

    @abstractmethod
    async def get_workout_types(user_id: int, is_active = None) -> list[tuple]:
        """Возвращает типы тренировок пользователя - активные, неактивные, все"""
        pass

    @abstractmethod
    async def set_active_workout_type(workout_type: int, is_active: bool) -> None:
        """Устанавливает флаг активности типа тренировки"""
        pass

    @abstractmethod
    async def delete_workout_type(workout_type: int) -> None:
        """Удаляет тип тренировки"""
        pass

    @abstractmethod
    async def get_name_workout_type(workout_type: int) -> str:
        """Возвращает имя типа тренировки"""
        pass

    @abstractmethod
    async def add_new_exercise_type(user_id: int, name: str) -> int:
        """Создает новый тип упражнения"""
        pass

    @abstractmethod
    async def start_workout(user_id: int, workout_type: int) -> int:
        """Фиксирует в БД страт тренировки"""
        pass

    @abstractmethod
    async def start_exercise(exercise_type: int, workout: int) -> int:
        """Записывает в БД старт упражнения"""
        pass

    @abstractmethod
    async def get_weight_workout(workout: int) -> list[tuple]:
        """Возвращает выполненые упражнения с весами для конкретной тренировки"""
        pass

    @abstractmethod
    async def end_workout(workout: int) -> None:
        """Фиксирует в БД конец тренировки"""
        pass

    @abstractmethod
    async def get_workout_exercises(workout_type: int) -> list[tuple]:
        """Возвращает типы упражнения, которые были в последней тренировке этого типа"""
        pass

    @abstractmethod
    async def get_latest_workout_ids(workout_type: int) -> list[int]:
        """Возвращает последние 3 id тренировок для типа тренировки"""
        pass

    @abstractmethod
    async def get_date_workout(workout: int) -> str:
        """Возвращает дату тренировки"""
        pass

    @abstractmethod
    async def update_exercise(exercise: int, weight: str) -> None:
        """Добавляет новый вес к упражнению"""
        pass

    @abstractmethod
    async def get_all_exercise_types(chat_id: int) -> list[tuple]:
        """Возвращает все типы упражнений"""
        pass

    @abstractmethod
    async def get_info_workout(workout: int) -> tuple:
        """Возвращает информацию о тренировке"""
        pass

    @abstractmethod
    async def get_exercise_history(exercise_type: int) -> list[tuple]:
        """Возвращает веса последних 5 упражнений определенного типа"""
        pass

    @abstractmethod
    async def delete_exercise(exercise: int) -> tuple:
        """Удаляет упражнение из тренировки"""
        pass