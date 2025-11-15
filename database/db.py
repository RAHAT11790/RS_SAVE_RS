import sqlite3
import os
from config import DB_NAME

class Database:
    
    def __init__(self, database_name):
        self.db_name = f"{database_name}.db"
        self._init_db()
    
    def _init_db(self):
        """ডাটাবেস টেবিল তৈরি করুন"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                session TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """ডাটাবেস কানেকশন পান"""
        return sqlite3.connect(self.db_name)
    
    def new_user(self, id, name):
        return {
            'id': id,
            'name': name,
            'session': None
        }
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR IGNORE INTO users (id, name, session) VALUES (?, ?, ?)',
            (user['id'], user['name'], user['session'])
        )
        conn.commit()
        conn.close()
    
    async def is_user_exist(self, id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (int(id),))
        user = cursor.fetchone()
        conn.close()
        return bool(user)
    
    async def total_users_count(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    async def get_all_users(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'name': row[1],
                'session': row[2]
            })
        conn.close()
        return users

    async def delete_user(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (int(user_id),))
        conn.commit()
        conn.close()

    async def set_session(self, id, session):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET session = ? WHERE id = ?',
            (session, int(id))
        )
        conn.commit()
        conn.close()

    async def get_session(self, id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT session FROM users WHERE id = ?', (int(id),))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

db = Database(DB_NAME)