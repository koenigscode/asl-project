import sqlite3
import json
import os

input_data = [
    ("./data/MSASL_train.json", "train"),
    ("./data/MSASL_test.json", "test"),
    ("./data/MSASL_val.json", "val")]

db_file = 'all-data.db'


def create_table(conn):
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS video_data (
        org_text TEXT,
        clean_text TEXT,
        start_time DECIMAL(10,3),
        signer_id INTEGER,
        signer INTEGER,
        start INTEGER,
        end INTEGER,
        file TEXT,
        label INTEGER,
        height DECIMAL(10,3),
        fps DECIMAL(10,3),
        end_time DECIMAL(10,3),
        url TEXT,
        text TEXT,
        box_1 DECIMAL(10,3),
        box_2 DECIMAL(10,3),
        box_3 DECIMAL(10,3),
        box_4 DECIMAL(10,3),
        width DECIMAL(10,3),
        data_type TEXT CHECK(data_type IN ('train', 'test', 'val'))
    )
    ''')


def insert_data(conn, data, data_type):
    cursor = conn.cursor()

    for item in data:
        box_1, box_2, box_3, box_4 = item['box']

        cursor.execute('''
        INSERT INTO video_data (
            org_text, clean_text, start_time, signer_id, signer, start, end, file,
            label, height, fps, end_time, url, text, box_1, box_2, box_3, box_4, width, data_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['org_text'], item['clean_text'], item['start_time'], item['signer_id'],
            item['signer'], item['start'], item['end'], item['file'],
            item['label'], item['height'], item['fps'], item['end_time'],
            item['url'], item['text'], box_1, box_2, box_3, box_4, item['width'], data_type
        ))

    conn.commit()


def get_most_common_signs(conn):
    cursor = conn.cursor()

    query = '''
        SELECT clean_text, COUNT(*) AS occurrences
        FROM video_data
        WHERE data_type = 'train'
        GROUP BY clean_text
        ORDER BY occurrences DESC
        LIMIT 20;
        '''

    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":

    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Database {db_file} already existed - deleted")

    conn = sqlite3.connect(db_file)

    create_table(conn)

    for file_name, data_type in input_data:
        with open(file_name, 'r') as f:
            data = json.load(f)
            insert_data(conn, data, data_type)

    print("Most frequent ASL signs in the training dataset:")
    for row in get_most_common_signs(conn):
        clean_text, occurrences = row
        print(f"{clean_text}: {occurrences}")

    print(f"Wrote all data to {db_file}")

    conn.close()
