import sqlite3, pathlib, bcrypt
DB_PATH=pathlib.Path(__file__).parent.parent/"database"/"users.db"
DB_PATH.parent.mkdir(exist_ok=True)
def init_db():
    conn=sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password_hash TEXT)')
    conn.commit();conn.close()
def register_user(name,email,password):
    init_db();conn=sqlite3.connect(DB_PATH)
    try:
        hashed=bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
        conn.execute("INSERT INTO users (name,email,password_hash) VALUES (?,?,?)",(name,email,hashed))
        conn.commit()
        return True,"Registered"
    except:
        return False,"Email exists"
    finally:
        conn.close()
def login_user(email,password):
    init_db();conn=sqlite3.connect(DB_PATH)
    cur=conn.execute("SELECT name,email,password_hash FROM users WHERE email=?",(email,))
    row=cur.fetchone();conn.close()
    if row and bcrypt.checkpw(password.encode(),row[2].encode()):
        return True,{"name":row[0],"email":row[1]}
    return False,None
