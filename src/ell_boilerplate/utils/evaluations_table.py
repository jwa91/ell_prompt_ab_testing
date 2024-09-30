import sqlite3
import ell

def initialize_evaluation_table():
    ell.init(store='./logdir')

    store = ell.get_store()

    conn_string = store.engine.url.database
    print(f"Using database at: {conn_string}")

    conn = sqlite3.connect(conn_string)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evaluation (
        id VARCHAR PRIMARY KEY,
        invocation_id VARCHAR NOT NULL,
        metric_name VARCHAR NOT NULL,
        metric_value FLOAT NOT NULL,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (invocation_id) REFERENCES invocation(id)
    )
    ''')

    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_evaluation_invocation_id ON evaluation(invocation_id)
    ''')

    conn.commit()
    conn.close()

    print("succes")

def main():
    initialize_evaluation_table()

if __name__ == "__main__":
    main()
