import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Substitua com as credenciais do seu banco MySQL
# Formato: mysql+pymysql://usuario:senha@host:porta/nome_do_banco

# Em produção, busca a URL fornecida pelo serviço (ex: Render, Railway).
# Localmente, continua utilizando o MySQL configurado.
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:Burrinho0808@127.0.0.1:3306/hortifruti_db")

# O SQLAlchemy exige 'postgresql://' mas provedores cloud geralmente criam variáveis como 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = DATABASE_URL

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
