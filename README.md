# postgres-dynamic - Python-PostgreSQL Dynamic Query Builder

Postgres dynamic is a simple query builder developed for internal usage. It currently supports select, insert, update, and delete statements.
The purpose of this library is for better managament and maintenance of the code used in our environment.

## Installation

<div class="termy">

```console
$ pip install postgres-dynamic

---> 100%
```

</div>

## Parameter Format:
- connection_object: Callable
    ```Python
    connection_object = psycopg2.connect(host,port,database,user,password) #object created from psycopg2.connect()
    ```
- where: List(dict)
    ```Python
    where = [
        {
            'column_name': 'some_column_name', 
            'value': 'some_value', # can accept str, int, list, or tuple
            'operator': 'some_operator', # can be omitted (accepted operators are =, >, <, >=, <=, IN),
            'conjunction': 'some_conjunction', # can be omitted, used when you need to specify more than one conditions and will link with next index value (accepted conjunctions are AND, OR)
        },
    ],
    ```

- main_table: Union[dict, str]  

    For **select** query
    ```Python
    main_table = {
        'table': 'some_table_name', 
        'alias': 'some_alias_for_table',
    },
    ```

    For **transaction** query
    ```Python
    main_table = 'some_table_name'
    ```

- join_table: List(dict)
    ```Python
    join_table = [
        {
            'table': 'some_table_name', 
            'alias': 'some_alias_for_table', 
            'join_method': 'join_method', # accepted join methods are (INNER, LEFT, RIGHT, FULL) 
            'on': 'matching_column_on_both_table',
        },
    ]
    ```

- column_name: List(str)
    ```Python
    column_name = ['some_column_name', 'some_column_name', 'some_column_name',]
    ```

- column_and_value: dict
    ```Python
    column_and_value = {
        'some_column_name': 'some_value', # for multiple values just provide more key:value pair 
    }
    ```

- order: dict
    ```Python
    order = {
        'some_column_name': 'ASC', # accepted order values are (ASC, DESC), for multiple order conditions just provide more key:value pair 
    }
    ```

## Usage & Code Samples

Example DB  

`table:` **employees**
| id  | first_name | last_name
| --- | --- | ---
|  1  | Alex | Garcia
|  2  | Joe | Black
|  3  | John | Doe
|  4  | Barry | Allen
|  5  | Charlie | Cox

`table:` **salaries**
| employee_id  | salary
| --- | --- 
|  1  | 120,000 
|  2  | 135,000 
|  3  | 150,000
|  4  | 180,000
|  5  | 120,000 

- SELECT

    - Single Select  
        Single select always return a single value from the query, based on `fetchone` in psycopg2 and returning a dictionary with `{column_name: value}` of the tables.
        <details>
        <summary>Show more...</summary>  

        Parameters:
        ```
        main_table #required
        where #required
        join_table #optional (if omitted it won't join to any table)
        column_name #optional (if omitted it will select all columns on the provided table)
        ```
        
        Code samples:
        ```Python
        # without joining table

        from postgres_dynamic import PGDGet
        import asyncio

        query_result = PGDGet.get_one(
            main_table={'table': 'employees'},
            where=[
                {'column_name': 'id', 'value': '1'},
            ],
            column_name=['first_name']
        )

        result = asyncio.run(query_result)
        print(result)

        # {'first_name': 'Alex'}
        ```

        ```Python
        # with join table salaries

        query_result = PGDGet.get_one(
            main_table={'table': 'employees', 'alias': 'emp'},
            join_table=[
                {'table': 'salaries', 'alias': 'sal', 'join_method': 'INNER', 'on': 'emp.id = sal.employee_id'}
            ],
            where=[
                {'column_name': 'id', 'value': '1'},
            ],
        )

        result = asyncio.run(query_result)
        print(result)

        # {'id': '1', 'first_name': 'Alex', 'last_name': 'Garcia', 'employee_id': '1', 'salary': 120000}
        ```
        </details>

    - Multi Select  
        Multi select always return a dict with key `data`, based on `fetchall` in psycopg2 and returning a list of dictionary with `{column_name: value}` of the tables.
        Parameters:
        <details>
        <summary>Show more...</summary>  

        ```
        main_table #required
        where #optional (if omitted no condition will be passed)
        join_table #optional (if omitted it won't join to any table)
        column_name #optional (if omitted it will select all columns on the provided table)
        order #optional (if omitted it won't sort the query)
        limit #optional (if a limit count is given, no more than that many rows will be returned but possibly fewer, if the query itself yields fewer rows)
        offset #optional (it used to skip that many rows before beginning to return rows)

        notes:
        - If both OFFSET and LIMIT appear, then OFFSET rows are skipped before starting to count the LIMIT rows that are returned
        - When using LIMIT, it is important to use an ORDER BY clause that constrains the result rows into a unique order. Otherwise you will get an unpredictable subset of the query's rows.
        - For paging, you can specify 0 or 1 for the starting point of the first page
        ```
        
        Code samples:
        ```Python
        from postgres_dynamic import PGDGet
        import asyncio

        query_result = PGDGet.get_all(
            main_table={'table': 'employees'},
            limit=3,
            offset=2
        )

        result = asyncio.run(query_result)
        print(result)
        
        # {'data': [{'id': '4', 'first_name': 'Barry', 'last_name': 'Allen'}, {'id': '5', 'first_name': 'Charlie', 'last_name': 'Cox'}]}
        ```
    </details>  

    - Select count   
        Select count always return a dict with key `total_data`, based on `SELECT COUNT(*)` in SQL and returning a dictionary with `{total_data: value}` of the query.
        Parameters:
        <details>
        <summary>Show more...</summary>  

        ```
        main_table #required
        where #optional (if omitted no condition will be passed)
        join_table #optional (if omitted it won't join to any table)
        ```
        
        Code samples:
        ```Python
        from postgres_dynamic import PGDGet
        import asyncio

        query_result = PGDGet.get_count(
            main_table={'table': 'employees'},
            where=[{'column_name': 'first_name', 'value': 'Alex'}]
        )

        result = asyncio.run(query_result)
        print(result)
        
        # {'total_data': 1}
        ```
    </details>  


- INSERT

    - Insert Statement  
        Insert will not return anyting, and will not saved changes to the database unless you specify `commit=True` in the parameters.
        <details>
        <summary>Show more...</summary>  

        Parameters:
        ```
        main_table #required
        column_and_value #required
        commit #optional (if omitted, default value will be False which will not saving any changes to database)
        ```
        
        Code samples:
        ```Python
        # with auto commit

        from postgres_dynamic import PGDTransaction
        import asyncio

        query_result = PGDTransaction.insert(
            main_table='employees',
            column_and_value={'id': 6, 'first_name': 'Harrison', 'last_name': 'Ford'},
            commit=True
        )

        result = asyncio.run(query_result)
        print(result)

        # None
        # will insert a new employee to the employees table
        ```

        ```Python
        # without auto commit

        query_result = PGDTransaction.insert(
            main_table='salaries',
            column_and_value={'employee_id': 6, 'salary': 250000},
        )

        result = asyncio.run(query_result)
        print(result)

        # None
        # will insert a new salary to the salaries table
        
        # save changes to the database
        connection_object.commit()

        ```

    </details>

- UPDATE

    - Update Statement  
        Update will not return anyting, and will not saved changes to the database unless you specify `commit=True` in the parameters.
        <details>
        <summary>Show more...</summary>  

        Parameters:
        ```
        main_table #required
        column_and_value #required
        where #required
        commit #optional (if omitted, default value will be False which will not saving any changes to database)
        ```
        
        Code samples:
        ```Python
        # with auto commit

        from postgres_dynamic import PGDTransaction
        import asyncio

        query_result = PGDTransaction.update(
            main_table='employees',
            column_and_value={'first_name': 'Tyler', 'last_name': 'Oakley'},
            where=[
                {'column_name': 'id', 'value': '6'},
            ],
            commit=True
        )

        result = asyncio.run(query_result)
        print(result)

        # None
        # will update employee first_name and last_name with id 6
        ```

        ```Python
        # without auto commit

        query_result = PGDTransaction.update(
            main_table='salaries',
            column_and_value={'salary': 450000},
            where=[
                {'column_name': 'employee_id', 'value': '6'},
            ],
        )

        result = asyncio.run(query_result)
        print(result)

        # None
        # will update the salary with employee_id 6
        
        # save changes to the database
        connection_object.commit()

        ```

    </details>  


- DELETE

    - Delete Statement  
        Delete will not return anyting, and will not saved changes to the database unless you specify `commit=True` in the parameters.
        <details>
        <summary>Show more...</summary>  

        Parameters:
        ```
        main_table #required
        where #required
        commit #optional (if omitted, default value will be False which will not saving any changes to database)
        ```
        
        Code samples:
        ```Python
        # with auto commit

        from postgres_dynamic import PGDTransaction
        import asyncio

        query_result = PGDTransaction.delete(
            main_table='salaries',
            where=[
                {'column_name': 'employee_id', 'value': '6'},
            ],
            commit=True
        )

        result = asyncio.run(query_result)
        print(result)

        # None
        # will delete salary data with employee_id 6
        ```

        ```Python
        # without auto commit

        query_result = PGDTransaction.delete(
            main_table='employees',
            where=[
                {'column_name': 'id', 'value': '6'},
            ],
        )

        result = asyncio.run(query_result)
        print(result)

        # None
        # will delete the employee with id 6
        
        # save changes to the database
        connection_object.commit()
        ```

    </details>