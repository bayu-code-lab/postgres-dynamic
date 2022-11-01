from typing import Awaitable
class PGDTransaction:
    @classmethod
    async def insert(cls, connection_object: any, main_table: str, column_and_value: dict, commit: bool = False) -> Awaitable[None]:
        """Dynamic query to insert certain table that can target several columns
        
        Params supplied for column_and_values are dict that contains key, value pair

        Example parameters: 
        connection_object = psycopg2.connect(database='postgres', host='localhost', user='postgres', password='password')
        
        main_table='employees',

        column_and_value={'id': 6, 'first_name': 'Harrison', 'last_name': 'Ford'},

        commit=True #optional, if omitted commit=False
        """
        try:
            column_keys = ', '.join([key for key in column_and_value.keys()])
            query_template = """
                INSERT INTO {main_table}({column_keys}) VALUES ({column_values})
            """
            query = query_template.format(main_table=main_table, column_keys=column_keys, column_values=', '.join(['%s']*(len(column_and_value))))
            value = tuple([value for value in column_and_value.values()])
            connection_object.cursor().execute(query, value)
            if commit:
                connection_object.commit()
            return
        except Exception as e:
            connection_object.rollback()
            raise e

    @classmethod
    async def update(cls, connection_object: any, main_table: str, column_and_value: dict, where: list, commit: bool = False) -> Awaitable[None]:
        """Dynamic query to update certain table that can takes multiple conditions and target several columns
        
        Example parameters: 
        connection_object = psycopg2.connect(database='postgres', host='localhost', user='postgres', password='password')
        
        main_table='employees',

        column_and_value={'id': 6, 'first_name': 'Tyler', 'last_name': 'Oakley'},

        commit=True #optional, if omitted commit=False

        where=[
            {'column_name': 'id', 'value': '1', 'operator': '=', 'conjunction': 'AND'}, #operator and conjunction can be omitted
        ] 
        #conjunction only required when providing more than one dictionary
        """
        try:
            column_query = ', '.join([key + ' = %s' for key in column_and_value.keys()])
            where_query=''
            for w in where:
                where_query += f' {w["column_name"]} {w["operator"]} %s' if w.get('operator') else f' {w["column_name"]} = %s'
                where_query += f' {w["conjunction"]}' if w.get('conjunction') else ' '

            query_template = """
                UPDATE {main_table} SET {columns} WHERE {where_query}
            """
            query = query_template.format(main_table=main_table, columns=column_query, where_query=where_query)
            update_values = tuple(value for value in column_and_value.values())
            where_values = tuple(wv['value'] for wv in where)
            value = update_values + where_values
            connection_object.cursor().execute(query, value)
            if commit:
                connection_object.commit()
            return
        except Exception as e:
            connection_object.rollback()
            raise e

    @classmethod
    async def delete(cls, connection_object: any, main_table: str, where: list, commit: bool = False) -> Awaitable[None]:
        """Dynamic query to delete data from certain table that can takes several conditions
        
        Example parameters: 
        connection_object = psycopg2.connect(database='postgres', host='localhost', user='postgres', password='password')
        
        main_table='employees',

        commit=True #optional, if omitted commit=False

        where=[
            {'column_name': 'id', 'value': '1', 'operator': '=', 'conjunction': 'AND'}, #operator and conjunction can be omitted
        ] 
        #conjunction only required when providing more than one dictionary
        """
        try:
            where_query=''
            for w in where:
                where_query += f' {w["column_name"]} {w["operator"]} %s' if w.get('operator') else f' {w["column_name"]} = %s'
                where_query += f' {w["conjunction"]}' if w.get('conjunction') else ' '

            query_template = """
                DELETE FROM {main_table} WHERE {where_query}
            """
            query = query_template.format(main_table=main_table, where_query=where_query)
            value = tuple(wv['value'] for wv in where)
            connection_object.cursor().execute(query, value)
            if commit:
                connection_object.commit()
            return
        except Exception as e:
            connection_object.rollback()
            raise e