import psycopg2

class PGDConnection:
    def __init__(self, connection_string: dict, query: str, values: tuple) -> None:
        self.query = query
        self.values = values
        self.connection = psycopg2.connect(
            host = connection_string['PG_HOST'],
            port = connection_string['PG_PORT'],
            database = connection_string['PG_DATABASE'],
            user = connection_string['PG_USER'],
            password = connection_string['PG_PASSWORD']
        )
        self.cursor = self.connection.cursor()

    def __enter__(self):
        self.cursor.execute(self.query, self.values)
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.close()
        self.cursor.close