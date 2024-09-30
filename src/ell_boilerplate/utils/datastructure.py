import sqlite3
import ell
import os

def initialize_ell():
    ell.init(store='./logdir')
    store = ell.get_store()
    return store.engine.url.database

def get_all_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

def write_table_schema_to_markdown(table_name, file, cursor):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    file.write(f"## Structuur van de tabel '{table_name}'\n\n")
    file.write("| Column ID | Name | Type | Not Null | Default Value | Primary Key |\n")
    file.write("|-----------|------|------|----------|---------------|-------------|\n")

    for column in columns:
        col_id, name, col_type, not_null, default_val, pk = column
        file.write(f"| {col_id} | {name} | {col_type} | {not_null} | {default_val if default_val else 'None'} | {pk} |\n")
    
    file.write("\n")

def main():
    db_path = initialize_ell()
    output_path = os.path.join(os.getcwd(), "table_structure.md")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = get_all_tables(cursor)

    with open(output_path, "w") as file:
        file.write("# Database Tabellen Structuur\n\n")
        for table in tables:
            write_table_schema_to_markdown(table, file, cursor)

    conn.close()
    print(f"Table structures have been written to {output_path}")

if __name__ == "__main__":
    main()
