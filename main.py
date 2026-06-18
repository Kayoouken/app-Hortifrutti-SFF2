from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import os

import models
import schemas
from database import engine, get_db

try:
    # Cria as tabelas no banco de dados (idealmente depois usaremos o Alembic para migrações)
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️ AVISO: Erro ao conectar com o banco de dados durante a inicialização: {e}")

app = FastAPI(title="Hortifruti PDV API")

# Lemos a variável de ambiente. Se não existir, libera o localhost do Vue.
cors_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,https://app-feirao-hortifruti.netlify.app")
CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",") if origin.strip()]

# FastAPI bloqueia allow_credentials=True quando usamos allow_origins=["*"].
# Ajustamos dinamicamente para evitar crash no servidor.
is_credentials_allowed = False if "*" in CORS_ORIGINS else True

# Configuração de CORS segura
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=is_credentials_allowed,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rotas de Unidades de Medida ---
@app.post("/unidades/", response_model=schemas.UnidadeMedidaResponse, tags=["Configurações"])
def criar_unidade_medida(unidade: schemas.UnidadeMedidaCreate, db: Session = Depends(get_db)):
    db_unidade = models.UnidadeMedida(**unidade.model_dump())
    db.add(db_unidade)
    try:
        db.commit()
        db.refresh(db_unidade)
        return db_unidade
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unidade ou sigla já cadastrada.")

@app.get("/unidades/", response_model=List[schemas.UnidadeMedidaResponse], tags=["Configurações"])
def listar_unidades(db: Session = Depends(get_db)):
    unidades = db.query(models.UnidadeMedida).all()
    return unidades

# --- Rotas de Produtos ---
@app.post("/produtos/", response_model=schemas.ProdutoResponse, tags=["Catálogo"])
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = models.Produto(**produto.model_dump())
    db.add(db_produto)
    try:
        db.commit()
        db.refresh(db_produto)
        return db_produto
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Código interno já existe.")

@app.get("/produtos/", response_model=List[schemas.ProdutoResponse], tags=["Catálogo"])
def listar_produtos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Retorna produtos já com seus respectivos preços (graças ao relationship configurado)
    produtos = db.query(models.Produto).offset(skip).limit(limit).all()
    return produtos

@app.put("/produtos/{produto_id}", response_model=schemas.ProdutoResponse, tags=["Catálogo"])
def atualizar_produto(produto_id: int, produto_update: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    
    db_produto.nome = produto_update.nome
    db_produto.descricao = produto_update.descricao
    try:
        db.commit()
        db.refresh(db_produto)
        return db_produto
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao atualizar o produto.")

@app.delete("/produtos/{produto_id}", tags=["Catálogo"])
def apagar_produto(produto_id: int, db: Session = Depends(get_db)):
    db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    try:
        db.delete(db_produto)
        db.commit()
        return {"detail": "Produto apagado com sucesso."}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não é possível apagar este produto pois ele já está vinculado a vendas no histórico.")

# --- Rotas de Preços (Foco na Atualização Expressa) ---
@app.post("/produtos/{produto_id}/precos/", response_model=schemas.ProdutoPrecoResponse, tags=["Preços"])
def vincular_preco_produto(produto_id: int, preco: schemas.ProdutoPrecoCreate, db: Session = Depends(get_db)):
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
        
    db_preco = models.ProdutoPreco(produto_id=produto_id, **preco.model_dump())
    db.add(db_preco)
    try:
        db.commit()
        db.refresh(db_preco)
        return db_preco
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Este produto já possui um preço para esta unidade de medida.")

@app.put("/precos/{preco_id}", response_model=schemas.ProdutoPrecoResponse, tags=["Preços"])
def atualizar_preco_expresso(preco_id: int, preco_update: schemas.ProdutoPrecoUpdate, db: Session = Depends(get_db)):
    db_preco = db.query(models.ProdutoPreco).filter(models.ProdutoPreco.id == preco_id).first()
    if not db_preco:
        raise HTTPException(status_code=404, detail="Preço não encontrado.")
    
    db_preco.preco_venda = preco_update.preco_venda
    try:
        db.commit()
        db.refresh(db_preco)
        return db_preco
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao atualizar o preço.")

# --- Rotas de Clientes ---
@app.post("/clientes/", response_model=schemas.ClienteResponse, tags=["Clientes"])
def criar_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = models.Cliente(**cliente.model_dump())
    db.add(db_cliente)
    try:
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="CPF ou CNPJ já cadastrado.")

@app.get("/clientes/", response_model=List[schemas.ClienteResponse], tags=["Clientes"])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clientes = db.query(models.Cliente).offset(skip).limit(limit).all()
    return clientes

# --- Rotas de Vendas (PDV) ---
@app.post("/vendas/", response_model=schemas.VendaResponse, tags=["Vendas"])
def registrar_venda(venda: schemas.VendaCreate, db: Session = Depends(get_db)):
    # 1. Separa os dados da venda dos itens
    venda_data = venda.model_dump(exclude={"itens"})
    db_venda = models.Venda(**venda_data)
    
    try:
        db.add(db_venda)
        db.flush() # Envia pro banco e obtém o db_venda.id, MAS NÃO finaliza a transação ainda
        
        soma_subtotais = 0
        
        # 2. Registra todos os itens vinculados a essa nova venda
        for item in venda.itens:
            db_item = models.ItemVenda(venda_id=db_venda.id, **item.model_dump())
            db.add(db_item)
            soma_subtotais += item.subtotal
            
        # Validação de segurança: O total enviado bate com a soma dos itens?
        if venda.valor_total != soma_subtotais:
            raise ValueError(f"O valor total da venda (R$ {venda.valor_total}) diverge da soma dos itens (R$ {soma_subtotais}).")
            
        # 3. Comita tudo de uma vez. Se falhar, faz o rollback da venda e dos itens.
        db.commit()
        db.refresh(db_venda)
        return db_venda
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        # Um erro de chave estrangeira (produto inexistente) ou qualquer outra falha cai aqui
        raise HTTPException(status_code=400, detail="Erro ao registrar a venda. Verifique a integridade dos dados enviados.")

@app.get("/vendas/", response_model=List[schemas.VendaResponse], tags=["Vendas"])
def listar_vendas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Retorna as vendas ordenadas da mais recente para a mais antiga
    vendas = db.query(models.Venda).order_by(models.Venda.data_venda.desc()).offset(skip).limit(limit).all()
    return vendas

@app.put("/vendas/{venda_id}", response_model=schemas.VendaResponse, tags=["Vendas"])
def atualizar_venda(venda_id: int, venda: schemas.VendaCreate, db: Session = Depends(get_db)):
    db_venda = db.query(models.Venda).filter(models.Venda.id == venda_id).first()
    if not db_venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada.")
        
    venda_data = venda.model_dump(exclude={"itens"})
    for key, value in venda_data.items():
        setattr(db_venda, key, value)
        
    # Limpa os itens antigos vinculados a esta venda para inserir os novos modificados
    db.query(models.ItemVenda).filter(models.ItemVenda.venda_id == venda_id).delete()
    
    soma_subtotais = 0
    for item in venda.itens:
        db_item = models.ItemVenda(venda_id=db_venda.id, **item.model_dump())
        db.add(db_item)
        soma_subtotais += item.subtotal
        
    if venda.valor_total != soma_subtotais:
        db.rollback()
        raise HTTPException(status_code=400, detail="O valor total da venda diverge da soma dos itens.")
        
    try:
        db.commit()
        db.refresh(db_venda)
        return db_venda
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao atualizar a venda. Verifique a integridade dos dados.")

@app.delete("/vendas/{venda_id}", tags=["Vendas"])
def apagar_venda(venda_id: int, db: Session = Depends(get_db)):
    db_venda = db.query(models.Venda).filter(models.Venda.id == venda_id).first()
    if not db_venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada.")
    try:
        db.delete(db_venda)
        db.commit()
        return {"detail": "Venda apagada com sucesso."}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao apagar a venda.")

# --- Rotas de Relatórios ---
@app.get("/relatorios/faturamento-diario", response_model=List[schemas.RelatorioFaturamentoDiario], tags=["Relatórios"])
def relatorio_faturamento_diario(db: Session = Depends(get_db)):
    """
    Gera um relatório de faturamento agrupado por dia, considerando apenas vendas 'CONCLUIDA'.
    """
    resultados = (
        db.query(
            func.date(models.Venda.data_venda).label("data"),
            func.sum(models.Venda.valor_total).label("faturamento_total"),
            func.count(models.Venda.id).label("quantidade_vendas")
        )
        .filter(models.Venda.status == "CONCLUIDA")
        .group_by(func.date(models.Venda.data_venda))
        .order_by(func.date(models.Venda.data_venda).desc())
        .all()
    )
    
    return [{"data": r.data, "faturamento_total": r.faturamento_total or 0, "quantidade_vendas": r.quantidade_vendas} for r in resultados]

# --- Rota Raiz (Health Check do Render) ---
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "online", "mensagem": "API do Hortifruti SFF2 funcionando perfeitamente!"}
