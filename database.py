import sqlite3

import jsonpickle
from pathlib import Path

from library.sqlite import SQLite


def setup_custom_types() -> type:
    """ Пользовательские типы данных для сохранения в БД """

    from library.node_editor import NodeFreezer

    def adapt_pyobject(obj: object) -> bytes:
        return jsonpickle.encode(obj)

    def convert_pyobject(s: bytes) -> object:
        return jsonpickle.decode(s)

    sqlite3.register_adapter(NodeFreezer.EditorState, adapt_pyobject)
    sqlite3.register_converter("PYOBJECT", convert_pyobject)

    return NodeFreezer.EditorState


NodeEditorState = setup_custom_types()


class Database(SQLite):

    def insert_node_editor_state(self, name: str, state: NodeEditorState) -> int:
        """ Добавить запись в таблицу node_editor_state """

        with self.connection() as conn:

            stmt = "INSERT INTO node_editor_state(name, state) VALUES (?, ?)"
            values = (name, state)
            conn.execute(stmt, values)

            stmt = "SELECT last_insert_rowid() AS rowid"
            cur = conn.execute(stmt)
            return cur.fetchone()["rowid"]

    def select_node_editor_states_info(self) -> list[dict]:
        """ Получить инфу о сохраненных состояниях node_editor_state """

        with self.connection() as conn:
            stmt = "SELECT rowid, name FROM node_editor_state"
            cur = conn.execute(stmt)
            return cur.fetchall()

    def select_node_editor_state(self, rowid: int) -> list[dict]:
        """ Получить одну запись из node_editor_state """

        with self.connection() as conn:
            stmt = "SELECT * FROM node_editor_state WHERE rowid = ?"
            cur = conn.execute(stmt, (rowid,))
            return cur.fetchone()

    def delete_node_editor_state(self, rowid: int):
        """ Удалить одну запись из node_editor_state """

        with self.connection() as conn:
            stmt = "DELETE FROM node_editor_state WHERE rowid = ?"
            conn.execute(stmt, (rowid,))


# запрос для инициализации таблиц БД
INIT_STMT = """
CREATE TABLE IF NOT EXISTS node_editor_state (
    name TEXT,
    state PYOBJECT
)
"""

db = Database(
    filepath=Path("main.db"),
    init_stmt=INIT_STMT
)
