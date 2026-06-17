const API_URL = "http://localhost:8000";

export const fetchProdutos = async () => {
  try {
    const response = await fetch(`${API_URL}/produtos/`);
    if (!response.ok) {
      throw new Error('Falha ao buscar produtos da API');
    }
    return await response.json();
  } catch (error) {
    console.error("Erro na API (fetchProdutos):", error);
    return [];
  }
};

export const criarProduto = async (produtoData) => {
  try {
    const response = await fetch(`${API_URL}/produtos/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(produtoData)
    });
    if (!response.ok) {
      throw new Error('Falha ao criar produto');
    }
    return await response.json();
  } catch (error) {
    console.error("Erro na API (criarProduto):", error);
    throw error;
  }
};

export const fetchUnidades = async () => {
  try {
    const response = await fetch(`${API_URL}/unidades/`);
    if (!response.ok) throw new Error('Falha ao buscar unidades');
    return await response.json();
  } catch (error) {
    console.error("Erro na API (fetchUnidades):", error);
    return [];
  }
};

export const vincularPreco = async (produtoId, precoData) => {
  try {
    const response = await fetch(`${API_URL}/produtos/${produtoId}/precos/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(precoData)
    });
    if (!response.ok) throw new Error('Falha ao vincular preço');
    return await response.json();
  } catch (error) {
    console.error("Erro na API (vincularPreco):", error);
    throw error;
  }
};