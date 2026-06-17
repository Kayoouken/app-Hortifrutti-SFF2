from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Substitua com as credenciais do seu banco MySQL
# Formato: mysql+pymysql://usuario:senha@host:porta/nome_do_banco

# Coloque sua senha real no lugar de SUA_SENHA_REAL. Se não tiver senha, use: mysql+pymysql://root@127.0.0.1:3306/hortifruti_db
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Burrinho0808@127.0.0.1:3306/hortifruti_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependência do FastAPI para injetar a sessão do banco nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
