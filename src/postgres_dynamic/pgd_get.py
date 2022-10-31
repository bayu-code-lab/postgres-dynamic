from typing import Awaitable, Optional
from datetime import datetime, timedelta
from postgres_dynamic.pgd_connection import PGDConnection

class PGDGet:
    @classmethod
    async def get_one(cls, connection_string: dict, main_table: dict, where: list, join_table:list = [], column_name: list = None) -> Awaitable[dict]:
        try:
            result = {}
            column_name = ','.join(column_name) if column_name else '*'
            query = """
                SELECT {column_name} FROM {main_table} {main_table_alias} {join_table} WHERE {where_query}
            """
            
            where_query=''
            for w in where:
                where_query += f' {w["column_name"]} {w["operator"]} %s' if w.get('operator') else f' {w["column_name"]} = %s'
                where_query += f' {w["conjunction"]}' if w.get('conjunction') else ' '

            join_query = ''
            for i in join_table:
                join_query += ' INNER JOIN' if i['join_method'] == 'INNER' else ' LEFT JOIN' if i['join_method'] == 'LEFT' else ' RIGHT JOIN'
                join_query += f' {i["table"]} {i["alias"]} ON {i["on"]}'

            query = query.format(column_name=column_name, main_table=main_table['table'], main_table_alias=main_table['alias'] if main_table.get('alias') else '', join_table=join_query, where_query=where_query)
            where_values = tuple(wv['value'] for wv in where)
            values = where_values
            with PGDConnection(connection_string, query, values) as cursor:
                column_name = [i[0] for i in cursor.description]
                data = cursor.fetchone()
                if data:
                    for a, b in zip(column_name, data):
                        result[a] = str(b + timedelta(hours=7)) if type(b) is datetime else b
            return result
        except Exception as e:
            raise e

    @classmethod
    async def get_all(cls, connection_string: dict, main_table: dict, where: list = [], join_table:list = [], order: dict = {}, column_name: list = None, limit: Optional[int] = None, offset: Optional[int] = None) -> Awaitable[dict]:
        try:
            result = []
            column_name = ','.join(column_name) if column_name else '*'
            query = """
                SELECT {column_name} FROM {main_table} {main_table_alias} {join_table} {where_query} {order_query} LIMIT %s OFFSET %s
            """
            where_query = ''
            if where:
                where_query += 'WHERE '
                for w in where:
                    where_query += f' {w["column_name"]} {w["operator"]} %s' if w.get('operator') else f' {w["column_name"]} = %s'
                    where_query += f' {w["conjunction"]}' if w.get('conjunction') else ' '

            order_query = ''
            if order:
                order_query = 'ORDER BY ' 
                order_query += ''.join([f'{k} {v}' for k,v in order.items()]) if len(order) == 1 else ', '.join([f'{k} {v}' for k,v in order.items()])

            join_query = ''
            for i in join_table:
                join_query += ' INNER JOIN' if i['join_method'] == 'INNER' else ' LEFT JOIN' if i['join_method'] == 'LEFT' else ' RIGHT JOIN'
                join_query += f' {i["table"]} {i["alias"]} ON {i["on"]}'

            query = query.format(column_name=column_name, main_table=main_table['table'], main_table_alias=main_table['alias'] if main_table.get('alias') else '', join_table=join_query, where_query=where_query, order_query=order_query)
            where_values = tuple(wv['value'] for wv in where)
            offset_value = (limit*(offset-1)) if offset else None
            values = where_values + (limit, offset_value)
            with PGDConnection(connection_string, query, values) as cursor:
                column_name = [i[0] for i in cursor.description]
                for i in cursor.fetchall():
                    data = {}
                    for a, b in zip(column_name, i):
                        data[a] = str(b + timedelta(hours=7)) if type(b) is datetime else b
                    result.append(data)
            return {'data': result}
        except Exception as e:
            raise e

    @classmethod
    async def get_count(cls, connection_string: dict, main_table: dict, where: list = [], join_table:list = []) -> Awaitable[dict]:
        try:
            result = []
            query = """
                SELECT COUNT(*) FROM {main_table} {main_table_alias} {join_table} {where_query}
            """

            where_query = ''
            if where:
                where_query += 'WHERE '
                for w in where:
                    where_query += f' {w["column_name"]} {w["operator"]} %s' if w.get('operator') else f' {w["column_name"]} = %s'
                    where_query += f' {w["conjunction"]}' if w.get('conjunction') else ' '

            join_query = ''
            for i in join_table:
                join_query += ' INNER JOIN' if i['join_method'] == 'INNER' else ' LEFT JOIN' if i['join_method'] == 'LEFT' else ' RIGHT JOIN'
                join_query += f' {i["table"]} {i["alias"]} ON {i["on"]}'
                
            query = query.format(main_table=main_table['table'], main_table_alias=main_table['alias'] if main_table.get('alias') else '', join_table=join_query, where_query=where_query)
            where_values = tuple(wv['value'] if isinstance(wv['value'], str) else tuple(wv['value']) for wv in where )
            values = where_values
            with PGDConnection(connection_string, query, values) as cursor:
                result = cursor.fetchone()[0]
            return {'total_data': result}
        except Exception as e:
            raise e