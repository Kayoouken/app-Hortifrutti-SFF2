<template>
  <div class="container">
    <header class="header">
      <div>
        <h2>Atualização Expressa de Preços</h2>
        <p class="subtitle">Altere os valores abaixo e pressione <kbd>Enter</kbd> (ou clique fora) para salvar.</p>
      </div>
      <button @click="carregarDados" class="btn-refresh">Recarregar</button>
    </header>

    <div v-if="carregando" class="loading">Carregando planilha...</div>

    <table v-else class="excel-table">
      <thead>
        <tr>
          <th class="col-codigo">Código</th>
          <th>Produto</th>
          <th class="col-unidade">Unidade</th>
          <th class="col-preco">Preço (R$)</th>
          <th class="col-status">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="linha in linhas" :key="linha.preco_id">
          <td class="center codigo">{{ linha.codigo_interno }}</td>
          <td>{{ linha.nome }}</td>
          <td class="center destaque">{{ linha.unidade_sigla }}</td>
          <td class="cell-input">
            <input
              type="number"
              step="0.01"
              v-model="linha.novo_preco"
              @change="salvarPreco(linha)"
              @keyup.enter="$event.target.blur()" 
            />
            <!-- O $event.target.blur() tira o foco ao dar Enter, o que automaticamente aciona o @change -->
          </td>
          <td class="center status-cell">
            <span v-if="linha.salvando" class="status saving">Salvando...</span>
            <span v-else-if="linha.sucesso" class="status success">✔ Salvo</span>
            <span v-else-if="linha.erro" class="status error">✖ Erro</span>
          </td>
        </tr>
        <tr v-if="linhas.length === 0">
          <td colspan="5" class="center sem-dados">Nenhum produto com preço vinculado foi encontrado.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const linhas = ref([]);
const carregando = ref(true);

const API_URL = "http://localhost:8000"; // Ajuste conforme necessário caso use api.js centralizada

const carregarDados = async () => {
  carregando.value = true;
  try {
    const response = await fetch(`${API_URL}/produtos/`);
    const produtos = await response.json();
    
    const dadosAchatados = [];
    // Achata os dados: transforma cada preço de cada unidade em uma linha independente
    produtos.forEach(produto => {
      produto.precos.forEach(preco => {
        dadosAchatados.push({
          preco_id: preco.id,
          codigo_interno: produto.codigo_interno,
          nome: produto.nome,
          unidade_sigla: preco.unidade.sigla,
          preco_original: preco.preco_venda,
          novo_preco: preco.preco_venda, // Variável que o input vai alterar
          salvando: false,
          sucesso: false,
          erro: false
        });
      });
    });
    linhas.value = dadosAchatados;
  } catch (error) {
    console.error("Erro ao buscar produtos:", error);
  } finally {
    carregando.value = false;
  }
};

const salvarPreco = async (linha) => {
  // Impede requisições de rede se o usuário clicar no campo e sair sem alterar o valor
  if (linha.novo_preco == linha.preco_original || linha.salvando) return;

  linha.salvando = true;
  linha.sucesso = false;
  linha.erro = false;

  try {
    const response = await fetch(`${API_URL}/precos/${linha.preco_id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preco_venda: parseFloat(linha.novo_preco) })
    });

    if (response.ok) {
      linha.preco_original = linha.novo_preco; // Sincroniza o valor de referência
      linha.sucesso = true;
      setTimeout(() => { linha.sucesso = false; }, 2500); // Esconde o aviso de sucesso após 2.5s
    } else {
      linha.erro = true;
    }
  } catch (error) {
    linha.erro = true;
    console.error("Erro ao atualizar preço:", error);
  } finally {
    linha.salvando = false;
  }
};

onMounted(() => {
  carregarDados();
});
</script>

<style scoped>
.container { max-width: 1200px; margin: 0 auto; padding: 20px; font-family: sans-serif; box-sizing: border-box; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header h2 { margin: 0; color: #334155; }
.subtitle { color: #666; font-size: 0.9rem; margin-top: 5px; }
.btn-refresh { padding: 8px 16px; background-color: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
.loading, .sem-dados { text-align: center; font-size: 1.1rem; color: #666; padding: 30px; }
.excel-table { width: 100%; border-collapse: collapse; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.1); border-radius: 4px; overflow: hidden; }
.excel-table th { background: #eceff1; border: 1px solid #cfd8dc; padding: 12px; text-align: left; font-weight: bold; color: #37474f; }
.excel-table td { border: 1px solid #cfd8dc; padding: 0; vertical-align: middle; color: #333; }
.excel-table td:not(.cell-input) { padding: 10px 12px; }
.center { text-align: center !important; }
.codigo { color: #888; font-family: monospace; font-size: 0.95rem; }
.destaque { font-weight: bold; color: #2e7d32; background-color: #f1f8e9; }
.col-codigo { width: 80px; } .col-unidade { width: 90px; } .col-preco { width: 140px; } .col-status { width: 100px; }
.cell-input input { width: 100%; height: 100%; box-sizing: border-box; border: none; padding: 12px; font-size: 1rem; text-align: right; background: #fafafa; color: #333; outline: none; font-family: monospace; font-weight: bold;}
.cell-input input:focus { background: #fff; box-shadow: inset 0 0 0 2px #4CAF50; }
.status-cell { font-size: 0.85rem; font-weight: bold; }
.saving { color: #ff9800; } .success { color: #4CAF50; } .erro { color: #f44336; }
</style>