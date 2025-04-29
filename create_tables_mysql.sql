-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Хост: 172.17.0.3
-- Время создания: Апр 05 2025 г., 07:56
-- Версия сервера: 8.0.41
-- Версия PHP: 8.2.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `gymbot`
--

-- --------------------------------------------------------

--
-- Структура таблицы `Exercises`
--

CREATE TABLE `Exercises` (
  `id` int NOT NULL,
  `type_id` int NOT NULL,
  `weight` varchar(255) NOT NULL,
  `id_workout` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `Exercise_types`
--

CREATE TABLE `Exercise_types` (
  `id` int NOT NULL,
  `user_id` bigint NOT NULL,
  `name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `Users`
--

CREATE TABLE `Users` (
  `chat_id` bigint NOT NULL,
  `name` varchar(255) NOT NULL,
  `age` int NOT NULL,
  `gender` varchar(50) NOT NULL,
  `height` int NOT NULL,
  `weight` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `Workouts`
--

CREATE TABLE `Workouts` (
  `id` int NOT NULL,
  `user_id` bigint NOT NULL,
  `type_id` int NOT NULL,
  `date` date NOT NULL,
  `start` time NOT NULL,
  `end` time DEFAULT NULL,
  `duration` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `Workout_types`
--

CREATE TABLE `Workout_types` (
  `id` int NOT NULL,
  `user_id` bigint NOT NULL,
  `name` varchar(255) NOT NULL,
  `is_active` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `Exercises`
--
ALTER TABLE `Exercises`
  ADD PRIMARY KEY (`id`),
  ADD KEY `type_id` (`type_id`),
  ADD KEY `id_workout` (`id_workout`);

--
-- Индексы таблицы `Exercise_types`
--
ALTER TABLE `Exercise_types`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Индексы таблицы `Users`
--
ALTER TABLE `Users`
  ADD PRIMARY KEY (`chat_id`);

--
-- Индексы таблицы `Workouts`
--
ALTER TABLE `Workouts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `type_id` (`type_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Индексы таблицы `Workout_types`
--
ALTER TABLE `Workout_types`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `Exercises`
--
ALTER TABLE `Exercises`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `Exercise_types`
--
ALTER TABLE `Exercise_types`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `Workouts`
--
ALTER TABLE `Workouts`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `Workout_types`
--
ALTER TABLE `Workout_types`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `Exercises`
--
ALTER TABLE `Exercises`
  ADD CONSTRAINT `Exercises_ibfk_1` FOREIGN KEY (`type_id`) REFERENCES `Exercise_types` (`id`),
  ADD CONSTRAINT `Exercises_ibfk_2` FOREIGN KEY (`id_workout`) REFERENCES `Workouts` (`id`) ON DELETE CASCADE;

--
-- Ограничения внешнего ключа таблицы `Exercise_types`
--
ALTER TABLE `Exercise_types`
  ADD CONSTRAINT `Exercise_types_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `Users` (`chat_id`);

--
-- Ограничения внешнего ключа таблицы `Workouts`
--
ALTER TABLE `Workouts`
  ADD CONSTRAINT `Workouts_ibfk_1` FOREIGN KEY (`type_id`) REFERENCES `Workout_types` (`id`),
  ADD CONSTRAINT `Workouts_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `Users` (`chat_id`);

--
-- Ограничения внешнего ключа таблицы `Workout_types`
--
ALTER TABLE `Workout_types`
  ADD CONSTRAINT `Workout_types_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `Users` (`chat_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
