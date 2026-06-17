from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

# --- Unidades de Medida ---
class UnidadeMedidaBase(BaseModel):
    """Dados base para Unidade de Medida"""
    sigla: str
    nome: str

class UnidadeMedidaCreate(UnidadeMedidaBase):
    pass

class UnidadeMedidaResponse(UnidadeMedidaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Preços dos Produtos ---
class ProdutoPrecoBase(BaseModel):
    """Dados base de vínculo de Preço"""
    unidade_medida_id: int
    preco_venda: Decimal

class ProdutoPrecoCreate(ProdutoPrecoBase):
    pass

class ProdutoPrecoUpdate(BaseModel):
    """Schema otimizado para a atualização expressa de preço"""
    preco_venda: Decimal

class ProdutoPrecoResponse(ProdutoPrecoBase):
    id: int
    produto_id: int
    unidade: UnidadeMedidaResponse
    model_config = ConfigDict(from_attributes=True)

# --- Produtos ---
class ProdutoBase(BaseModel):
    """Dados base do Produto"""
    codigo_interno: str
    nome: str
    descricao: Optional[str] = None
    ativo: bool = True

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoResponse(ProdutoBase):
    id: int
    criado_em: datetime
    precos: List[ProdutoPrecoResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# --- Clientes ---
class ClienteBase(BaseModel):
    """Dados base do Cliente"""
    nome: str
    cpf_cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    criado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Itens de Venda (PDV) ---
class ItemVendaBase(BaseModel):
    """Dados de um item da venda com preço congelado"""
    produto_id: int
    unidade_medida_id: int
    quantidade: Decimal
    preco_unitario_aplicado: Decimal
    subtotal: Decimal

class ItemVendaCreate(ItemVendaBase):
    pass

class ItemVendaResponse(ItemVendaBase):
    id: int
    venda_id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- Vendas (PDV) ---
class VendaBase(BaseModel):
    """Cabeçalho da venda"""
    cliente_id: Optional[int] = None
    valor_total: Decimal
    status: str = "CONCLUIDA"

class VendaCreate(VendaBase):
    itens: List[ItemVendaCreate] # Permite criar a venda já com os itens aninhados no JSON

class VendaResponse(VendaBase):
    id: int
    data_venda: datetime
    itens: List[ItemVendaResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# --- Relatórios ---
class RelatorioFaturamentoDiario(BaseModel):
    """Relatório agrupado por dia"""
    data: date
    faturamento_total: Decimal
    quantidade_vendas: int

    model_config = ConfigDict(from_attributes=True)
