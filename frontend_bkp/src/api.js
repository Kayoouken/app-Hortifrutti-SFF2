const API_URL = 'http://localhost:8000';

export async function fetchProdutos() {
    try {
        const response = await fetch(`${API_URL}/produtos/`);
        if (!response.ok) throw new Error('Erro ao buscar produtos da API');
        return await response.json();
    } catch (error) {
        console.error("Erro na comunicação com a API:", error);
        return [];
    }
}