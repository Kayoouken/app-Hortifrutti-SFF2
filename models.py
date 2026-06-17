from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class Produto(Base):
    """Catálogo base de produtos. Não contém informações de preço e unidade."""
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_interno = Column(String(50), unique=True, index=True, nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, server_default=func.now())

    # Relacionamento com os preços
    precos = relationship("ProdutoPreco", back_populates="produto", cascade="all, delete-orphan")

class UnidadeMedida(Base):
    """Tipos de medição padronizados para o hortifruti (ex: KG, UN, CX)."""
    __tablename__ = "unidades_medida"

    id = Column(Integer, primary_key=True, index=True)
    sigla = Column(String(5), unique=True, nullable=False)
    nome = Column(String(50), nullable=False)

class ProdutoPreco(Base):
    """Tabela de vínculo: Define o preço de um produto de acordo com sua unidade de medida."""
    __tablename__ = "produto_precos"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False)
    unidade_medida_id = Column(Integer, ForeignKey("unidades_medida.id"), nullable=False)
    preco_venda = Column(Numeric(10, 2), nullable=False)

    # Garante que um produto não terá a mesma unidade cadastrada mais de uma vez (Ex: Dois preços de KG soltos)
    __table_args__ = (UniqueConstraint('produto_id', 'unidade_medida_id', name='uq_produto_unidade'),)

    produto = relationship("Produto", back_populates="precos")
    unidade = relationship("UnidadeMedida")

class Cliente(Base):
    """Cadastro de clientes."""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf_cnpj = Column(String(20), unique=True, index=True, nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    criado_em = Column(DateTime, server_default=func.now())

    vendas = relationship("Venda", back_populates="cliente")

class Venda(Base):
    """Cabeçalho de registro de Venda (PDV)."""
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True) # Pode ser nulo para vendas de balcão
    data_venda = Column(DateTime, server_default=func.now())
    valor_total = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="CONCLUIDA")

    cliente = relationship("Cliente", back_populates="vendas")
    itens = relationship("ItemVenda", back_populates="venda", cascade="all, delete-orphan")

class ItemVenda(Base):
    """Itens da venda. O preço unitário é congelado para manter o histórico."""
    __tablename__ = "itens_venda"

    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas.id", ondelete="CASCADE"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    unidade_medida_id = Column(Integer, ForeignKey("unidades_medida.id"), nullable=False)
    quantidade = Column(Numeric(10, 3), nullable=False)
    preco_unitario_aplicado = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto")
    unidade = relationship("UnidadeMedida")
