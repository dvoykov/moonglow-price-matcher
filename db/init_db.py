import sqlite3
from sqlite3 import Error
from config import db_params

def create_database() -> int:
    conn = sqlite3.connect(db_params['db_file'])

    cursor = conn.cursor()

    query1 = """
        create table if not exists products (
            id integer primary key autoincrement,
            source text not null,
            url text not null,
            name text not null,
            description text not null,
            price real not null,
            image_url text not null,
            name_emb blob,
            descr_emb blob
        );
    """

    query2 = "create unique index products_source_idx on products (source, url);"

    try:
        # create product table
        cursor.execute(query1)

        # add uq index on source/url columns
        cursor.execute(query2)

        conn.commit()
        print('The database was created successfully.')

    except Error as e:
        print(f'The sqlite error "{e}" occurred.')
    except Exception as e:
        print(f'The error "{e}" occurred')
    finally:
        conn.close()

if __name__ == '__main__':
    create_database()