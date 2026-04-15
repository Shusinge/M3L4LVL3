import sqlite3
from config import DATABASE

# Data awal untuk mengisi tabel secara otomatis
skills = [ (skill,) for skill in ['Python', 'SQL', 'API', 'Discord', 'Luau', 'JSON']]
statuses = [ (status,) for status in ['Pembuatan Prototipe', 'Dalam Pengembangan', 'Selesai, siap digunakan', 'Diperbarui', 'Selesai, tapi tidak sedang dilanjutkan']]

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            # Tabel Status
            conn.execute('''CREATE TABLE IF NOT EXISTS status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT UNIQUE
                        )''')
            
            # Tabel Skills
            conn.execute('''CREATE TABLE IF NOT EXISTS skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT UNIQUE
                        )''')

            # Tabel Proyek
            conn.execute('''CREATE TABLE IF NOT EXISTS projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''') 

            # Tabel Penghubung Proyek & Skills (Many-to-Many)
            conn.execute('''CREATE TABLE IF NOT EXISTS project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
                            PRIMARY KEY (project_id, skill_id)
                        )''')
            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    
    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
        
    def default_insert(self):
        # Insert skill default
        sql_skill = 'INSERT OR IGNORE INTO skills (skill_name) values(?)'
        self.__executemany(sql_skill, skills)
        
        # Insert status default
        sql_status = 'INSERT OR IGNORE INTO status (status_name) values(?)'
        self.__executemany(sql_status, statuses)

    # --- FUNGSI INSERT ---
    def insert_project(self, data):
        sql = """INSERT INTO projects (user_id, project_name, url, status_id) 
                 VALUES (?, ?, ?, ?)"""
        self.__executemany(sql, data)

    def insert_skill(self, user_id, project_name, skill):
        sql_p = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        res_p = self.__select_data(sql_p, (project_name, user_id))
        
        sql_s = 'SELECT skill_id FROM skills WHERE skill_name = ?'
        res_s = self.__select_data(sql_s, (skill,))
        
        if res_p and res_s:
            project_id = res_p[0][0]
            skill_id = res_s[0][0]
            sql_ps = 'INSERT OR IGNORE INTO project_skills VALUES(?, ?)'
            self.__executemany(sql_ps, [(project_id, skill_id)])

    # --- FUNGSI UPDATE (YANG BARU) ---
    def update_project_status(self, user_id, project_name, new_status_id):
        sql = "UPDATE projects SET status_id = ? WHERE project_name = ? AND user_id = ?"
        self.__executemany(sql, [(new_status_id, project_name, user_id)])

    def update_project_detail(self, param, value, project_name, user_id):
        # param bisa berisi 'description', 'url', atau 'project_name'
        sql = f"UPDATE projects SET {param} = ? WHERE project_name = ? AND user_id = ?"
        self.__executemany(sql, [(value, project_name, user_id)])

    # --- FUNGSI DELETE (YANG BARU) ---
    def delete_project(self, user_id, project_id):
        sql = "DELETE FROM projects WHERE user_id = ? AND project_id = ?"
        self.__executemany(sql, [(user_id, project_id)])

    def delete_status(self, status_id):
        # Menghapus status berdasarkan ID
        sql = "DELETE FROM status WHERE status_id = ?"
        self.__executemany(sql, [(status_id,)])

    # --- FUNGSI SELECT / GET ---
    def get_statuses(self):
        return self.__select_data("SELECT * FROM status")

    def get_status_id(self, status_name):
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        return res[0][0] if res else None

    def get_projects(self, user_id):
        sql = "SELECT * FROM projects WHERE user_id = ?"
        return self.__select_data(sql, (user_id,))
        
    def get_project_info(self, user_id, project_name):
        sql = """
            SELECT project_name, description, url, status_name FROM projects 
            JOIN status ON status.status_id = projects.status_id
            WHERE project_name=? AND user_id=?
        """
        return self.__select_data(sql, (project_name, user_id))

    def get_project_skills(self, project_name):
        sql = '''SELECT skill_name FROM projects 
                 JOIN project_skills ON projects.project_id = project_skills.project_id 
                 JOIN skills ON skills.skill_id = project_skills.skill_id 
                 WHERE project_name = ?'''
        res = self.__select_data(sql, (project_name,))
        return ', '.join([x[0] for x in res])

# --- MENJALANKAN PROGRAM ---
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.default_insert()
    print("Database siap digunakan!")