from __future__ import annotations
import os
import sqlite3 as sql
from typing import (
    Optional,
    TypeVar,
    Union,
    Tuple,
    List,
    Dict,
    Any,
)


__all__ = (
    # Main objects
    "DB",
    "Row",
    "Table",
    "Datatype",
    # Helper functions
    "escape",
    "make_condition",
    "get_values",
    "get_set_values",
)


T = TypeVar("T")
PK = "pk"


def escape(value: Any) -> str:
    """Escape invalid characters from sql queries

    :param value:
    :type value: Any
    :return: An escaped/safe string to be part of an sql query
    :rtype: str
    """
    v = ""
    if isinstance(value, str):
        for c in value:
            if c in "'":
                v += f"'{c}"
            else:
                v += c
        return f"'{v}'"
    else:
        return str(value)


def make_condition(**vars: Any) -> str:
    """Make an sql condition based on the `vars`

    ```
        >>> # Example
        >>> make_condition(name='john', age=15)
        'name=john AND age=15'
    ```
    :rtype: str
    """
    values = []
    for i, v in vars.items():
        val = "%s=%s" % (i, escape(v))
        values.append(val)
    return " AND ".join(values)


def get_values(**vars: Any) -> str:
    """Make an sql statement based on the values of `vars`
    ```
        >>> # Example
        >>> get_values(name='john', age=15)
        'john,\\n15'
    ```
    :rtype: str
    """
    values = []
    for i, v in vars.items():
        values.append(escape(v))
    return ",\n".join(values)


def get_set_values(**vars: Any) -> str:
    """Make an sql statement based on the values of `vars`
    ```
        >>> # Example
        >>> get_set_values(name='john', age=15)
        'name = john,\\nage=15'
    ```
    :rtype: str
    """
    values = []
    for i, v in vars.items():
        if i != PK:
            val = f"{i} = {escape(v)}"
            values.append(val)
    return f"    {',%s    '.join(values)}" % ("\n",)


class Datatype:
    ID = "INTEGER PRIMARY KEY"
    NULL = None
    INT = "INTEGER"
    INT_NOT_NULL = "INTEGER NOT NULL"
    REAL = "REAL"
    REAL_NOT_NULL = "REAL NOT NULL"
    STR = "TEXT"
    STR_NOT_NULL = "TEXT NOT NULL"
    BLOB = "BLOB"
    BLOB_NOT_NULL = "BLOB NOT NULL"


class ConnectionManager:
    def __init__(self, db: str) -> None:
        self.db = db
        self._connection = sql.connect(self.db)

    def __enter__(self) -> sql.Connection:
        return self._connection

    def __exit__(self, *args: Any) -> None:
        self._connection.commit()
        self._connection.close()


class Shared:
    def __init__(self, path: str) -> None:
        self.path = path

    def execute(self, query: str, show_query: bool) -> List[Any]:
        try:
            if show_query:
                print(query)
                print("--")
            with ConnectionManager(self.path) as conn:
                cur = conn.execute(query)
                data = cur.fetchall()
            return data
        except:
            print(query)
            exit()


## SQLITE WRAPPER IMPLEMENTATION ##


class Row(Shared):
    def __init__(self, table_name: str, db_path: str, **attrs: Any) -> None:
        self._table_name = table_name
        self._db_path = db_path
        super().__init__(self._db_path)
        for name, value in attrs.items():
            self.__dict__[name] = value

    def __eq__(self, row: Row) -> bool:  # type: ignore
        for key, value in self.items():
            if value != row[key]:
                return False
        return True

    def __str__(self) -> str:
        spaces_len = 4
        spaces = " " * spaces_len
        data = self._remove_object_vars()
        row = ""
        # for col_name in data:
        #     col = f"{spaces}{col_name}{spaces}|"
        #     row += col

        row += "\n"
        for col_name, col_val in data.items():
            col_name_len = len(col_name)
            col_val_len = len(str(col_val))
            total_space = col_name_len + (spaces_len * 2)

            if len(str(col_val)) > total_space:
                col = f"{col_val[:total_space-4]}... |"
            else:
                extra_spaces = " " * (total_space - col_val_len)
                col = f"{col_val}{extra_spaces}|"

            row += col
        return row

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> Row:
        self.__n = 0
        return self

    def __next__(self) -> Any:
        keys = tuple(self.__dict__.keys())[:-1]  # Remove the `self.__n`
        if self.__n == len(keys):
            raise StopIteration
        data = keys[self.__n]
        self.__n += 1
        return data

    def __getitem__(self, __k: Any) -> Any:
        return self.__dict__[__k]

    def _remove_object_vars(self) -> Dict[Any, Any]:
        items = self.__dict__.copy()
        to_remove = tuple(
            filter(lambda i: i.startswith("_") or i == "path", self.__dict__.copy())
        )
        for item in to_remove:
            items.pop(item)
        return items

    def save(self, show_query: bool = False) -> None:
        condition = get_values(**self)
        keys = ",".join(map(lambda i: f"'{i}'", self.keys()))
        query = f"INSERT INTO {self._table_name} ({keys}) VALUES ({condition})"
        self.execute(query, show_query)

    def values(self) -> Tuple[Any, ...]:
        return tuple(self.__dict__.values())

    def keys(self) -> Tuple[Any, ...]:
        keys = tuple(k for (k, _) in self.items())
        return keys

    def dict(self) -> Dict[Any, Any]:
        return dict(self.items())

    def items(self) -> Any:
        items = self._remove_object_vars()
        return items.items()

    def delete(self, show_query: bool = False) -> None:
        values = []
        for i, v in self.items():
            val = "%s=%s" % (i, escape(v))
            values.append(val)
        query = f"DELETE FROM {self._table_name} WHERE {' AND '.join(values)}"
        self.execute(query, show_query)

    def edit(self, show_query: bool = False) -> None:
        pk = self.pk  # type: ignore
        query = f"""UPDATE {self._table_name}
SET
{get_set_values(**self)}
WHERE
    {PK}={pk}
        """
        self.execute(query, show_query)


class Table(Shared):
    def __init__(
        self, db_path: str, name: str, rows: List[Row], col_names: List[str]
    ) -> None:
        self._col_names = col_names
        self._db_path = db_path
        self.name = name
        self.rows = rows
        super().__init__(self._db_path)

    def __str__(self) -> str:
        table = ""
        spaces_len = 4
        spaces = " " * spaces_len

        for col_name in self._col_names:
            cols = f"{spaces}{col_name}{spaces}|"
            table += cols
        for row in self.rows:
            table += f"{row}"
        return table

    def __contains__(self, row: Row) -> bool:
        return row in self.rows

    def __eq__(self, __value: Table) -> bool:  # type: ignore
        return self.name == __value.name and self.rows == __value.rows

    def make_row(self, **attrs: Any) -> Row:
        """Make a row that is bound to this `self` instance
        ```
            >>> # Example
            >>> self.make_row(name='john', age=15)
            Row(name='john', age=15, ...)
        ```
        :rtype: Row
        """
        return Row(
            self.name,
            self._db_path,
            **attrs,
        )

    def get_row(self, **where: Any) -> Optional[Row]:
        """Get a saved row object from the table
        ```
            >>> # Example
            >>> self.get_row(name='john', age=15)
            Row(name='john', age=15, pk=n, ...)
        ```
        :rtype: Row
        """
        for row in self.rows:
            if all(i in row.dict() for i in where):
                return row
        return None

    def filter_rows(self, **where: Any) -> Tuple[Row, ...]:
        rows = []
        for row in self.rows:
            if all(i in row.dict() for i in where):
                rows.append(row)
        return tuple(rows)

    def drop(self, show_query: bool = False) -> None:
        query = f"DROP TABLE IF EXISTS {self.name}"
        self.execute(query, show_query)

    def clear(self, show_query: bool = False) -> None:
        for row in self.rows:
            row.delete(show_query)


class DB(Shared):
    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(self.path)

    def __str__(self) -> str:
        db = ""
        seperator = "\n"
        for table in self.get_tables():
            db += seperator
            db += f"{table.name}\n"
            db += f"{table}\n"
        return db

    def col_names(self, table_name: str) -> List[str]:
        """Get a list of the column names bound on the `table_name`

        :param table_name: The name of the table
        :type table_name: str
        :rtype: List[str]
        """
        with ConnectionManager(self.path) as cur:
            data = cur.execute(f"SELECT * FROM {table_name}")
            names = [desc[0] for desc in data.description]
        return names

    def get_tables(self, show_query: bool = False) -> Tuple[Table, ...]:
        """Get all the tables bound to the `self` instance
        :rtype: Tuple[Table]
        """
        tables = []

        table_names = self.execute(
            "SELECT name FROM sqlite_schema WHERE type='table'", show_query
        )
        for table_name in table_names:
            db_rows = self.execute(f"SELECT * FROM {table_name[0]}", show_query)
            col_names = self.col_names(table_name[0])
            rows = []
            for col_vals in db_rows:
                row = {
                    col_name: col_val
                    for (col_name, col_val) in zip(col_names, col_vals)
                }
                rows.append(Row(table_name[0], self.path, **row))
            tables.append(Table(self.path, table_name[0], rows, col_names))
        return tuple(i for i in tables)

    def get_table(
        self, name: str, default: Optional[T] = None
    ) -> Union[Table, Optional[T]]:
        """Get a certain table from the `self` instance

        :param name: The name of the table
        :type name: str
        :param default: Default return value in case the table does not exists, defaults to None
        :type default: T, optional
        :rtype: Union[Table, T]
        """
        for table in self.get_tables():
            if name == table.name:
                return table
        return default

    def create_table(
        self, table_name: str, show_query: bool = False, **cols: str
    ) -> Table:
        """Create a table and save it in the `self` instance

        :param table_name: The name of the new table
        :type table_name: str
        :rtype: Table
        """
        cols[PK] = Datatype.ID
        values = []
        for col_name, col_val in cols.items():
            values.append(f"\t{col_name} {col_val}")
        values_as_query = ",\n".join(values)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (\n{values_as_query}\n);"
        self.execute(query, show_query)
        col_names = [i[0] for i in cols.items()]
        return Table(self.path, table_name, [], col_names)

    def clear_tables(self, show_query: bool = False) -> None:
        for table in self.get_tables():
            table.clear(show_query)

    def purge(self) -> None:
        os.remove(self.path)


if __name__ == "__main__":
    db = DB("db.sqlite3")
    e = [
        ["pantelis", 15],
        ["john", 24],
        ["Mary", 25],
    ]

    t = db.create_table("employees", name=Datatype.STR, age=Datatype.INT)
    for i in e:
        row = t.make_row(name=i[0], age=i[1])
        row.save()
    print(db)
    db.purge()
