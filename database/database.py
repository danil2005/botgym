from config_data.config import config

if config.type_db == 'sqlite':
    from database.database_sqlite import DataBaseSQLite
    database_obj = DataBaseSQLite()
elif config.type_db == 'mysql':
    from database.database_mysql import DataBaseMySQL
    database_obj = DataBaseMySQL(config.data_base)
else:
    raise Exception('Database type error')