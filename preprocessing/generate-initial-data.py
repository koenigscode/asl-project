import shutil
import argparse
import sqlite3


def copy_db(source, target):
    try:
        shutil.copy(source, target)
    except Exception as e:
        print(f"Error copying database: {e}")


def delete_rows_except(conn, table_name, clean_texts_to_keep):
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(clean_texts_to_keep))

    query = f'''
    DELETE FROM {table_name}
    WHERE clean_text NOT IN ({placeholders})
    '''

    cursor.execute(query, clean_texts_to_keep)
    conn.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate the initial database file")
    parser.add_argument("source_db", help="The source DB with all data")
    parser.add_argument(
        "target_db", help="The DB that shall be generated (the resulting initial data)")
    parser.add_argument("clean_texts", nargs='+',
                        help="List of clean_text to put into the intial dataset")
    args = parser.parse_args()

    print(f"Using database {args.source_db}")
    print(f"Creating database {args.target_db}")

    copy_db(args.source_db, args.target_db)

    conn = sqlite3.connect(args.target_db)
    delete_rows_except(conn, "video_data", args.clean_texts)
    conn.close()
