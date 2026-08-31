import sqlite3

def get_db_connection():
    conn = sqlite3.connect('chatbot.db', check_same_thread=False, timeout=10.0)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            thread_id TEXT PRIMARY KEY,
            thread_name TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    return conn

def get_next_thread_id():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT thread_id FROM threads WHERE thread_id LIKE 'thread%'")
        rows = cursor.fetchall()
        max_num = 0
        for r in rows:
            try:
                num = int(r[0].replace('thread', ''))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
        return f"thread{max_num + 1}"
    finally:
        conn.close()

def save_thread(thread_id, thread_name):
    conn = get_db_connection()
    try:
        conn.execute('INSERT OR IGNORE INTO threads (thread_id, thread_name) VALUES (?, ?)', (thread_id, thread_name))
        conn.commit()
    finally:
        conn.close()

def retrieve_all_threads():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Order by updated_at descending so the most recently active chats appear first
        cursor.execute('SELECT thread_id, thread_name FROM threads ORDER BY updated_at DESC')
        rows = cursor.fetchall()
        return [{'thread_id': r[0], 'thread_name': r[1]} for r in rows]
    finally:
        conn.close()

def update_thread_time(thread_id):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE threads SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = ?", (thread_id,))
        conn.commit()
    except Exception as e:
        print(f"Error updating thread time: {e}")
    finally:
        conn.close()

def remove_thread(thread_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM threads WHERE thread_id = ?', (thread_id,))
        # Also clean up langgraph checkpoints to free space
        conn.execute('DELETE FROM checkpoints WHERE thread_id = ?', (thread_id,))
        conn.execute('DELETE FROM writes WHERE thread_id = ?', (thread_id,))
        conn.commit()
    except Exception as e:
        print(f"Error removing thread from database: {e}")
    finally:
        conn.close()
