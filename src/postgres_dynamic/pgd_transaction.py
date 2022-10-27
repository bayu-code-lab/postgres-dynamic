from typing import Awaitable
class PGDTransaction:
    @classmethod
    async def insert(cls, connection_object: any, main_table: str, column_and_value: dict, commit: bool = False) -> Awaitable[None]:
        """Dynamic query to insert certain table that can target several columns
        
        Params supplied for column_and_values are dict that contains key, value pair

        Usage: 
        example query -> INSERT INTO table(col_1, col_2) VALUES (val_1, val_2)
        input params ex-> column_and_value = {col_1: value_1, col_2: value_2}
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
        
        Params supplied for column_and_values and condition are dict that contains key, value pair
        Multiple conditions are concatenated in query using 'AND' clause
        """
        try:
            column_query = ', '.join([key + ' = %s' for key in column_and_value.keys()])
            where_query=''
            for w in where:
                where_query += f' {w["column_name"]} {w["operator"]} %s' if w.get('operator') else f' {w["column_name"]} = %s'
                where_query += f' {w["conjuntion"]}' if w.get('conjuntion') else ' '

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
        
        Params supplied for conditions are dict that contains key, value pair
        Multiple conditions are concatenated in query using 'AND' clause
        """
        try:
            where_query=''
            for w in where:
                where_query += f' {w["column_name"]} {w["operator"]} %s' if w.get('operator') else f' {w["column_name"]} = %s'
                where_query += f' {w["conjuntion"]}' if w.get('conjuntion') else ' '

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