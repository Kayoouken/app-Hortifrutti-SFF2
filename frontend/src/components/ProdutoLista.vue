<template>
  <div class="container">
    <header class="header">
      <h2>Catálogo de Produtos e Preços</h2>
      <button @click="carregarProdutos" class="btn-refresh">Atualizar</button>
    </header>

    <div v-if="carregando" class="loading">Carregando produtos...</div>
    
    <div v-else class="grid-produtos">
      <div v-for="produto in produtos" :key="produto.id" class="card-produto">
        <div class="card-header">
          <span class="codigo">#{{ produto.codigo_interno }}</span>
          <h3 class="nome">{{ produto.nome }}</h3>
        </div>
        
        <div class="card-body">
          <p class="descricao">{{ produto.descricao || 'Sem descrição' }}</p>
          
          <div class="precos-lista">
            <div v-for="preco in produto.precos" :key="preco.id" class="preco-tag">
              <span class="unidade">{{ preco.unidade.sigla }}:</span>
              <span class="valor">R$ {{ parseFloat(preco.preco_venda).toFixed(2).replace('.', ',') }}</span>
            </div>
            <div v-if="produto.precos.length === 0" class="sem-preco">
              Nenhum preço vinculado
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { fetchProdutos } from '../api';

const produtos = ref([]);
const carregando = ref(true);

const carregarProdutos = async () => {
  carregando.value = true;
  produtos.value = await fetchProdutos();
  carregando.value = false;
};

// Carrega os produtos assim que o componente é montado na tela
onMounted(() => {
  carregarProdutos();
});
</script>

<style scoped>
.container { max-width: 1200px; margin: 0 auto; padding: 20px; font-family: sans-serif; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.btn-refresh { padding: 8px 16px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
.loading { text-align: center; font-size: 1.2rem; color: #666; margin-top: 50px; }

/* Layout Responsivo: Grid que se adapta ao celular ou monitor */
.grid-produtos { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
  gap: 20px; 
}

.card-produto { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.card-header { background: #f8f9fa; padding: 15px; border-bottom: 1px solid #eee; display: flex; align-items: baseline; gap: 10px;}
.codigo { font-size: 0.8rem; color: #888; font-weight: bold; }
.nome { margin: 0; font-size: 1.2rem; color: #333; }
.card-body { padding: 15px; }
.descricao { font-size: 0.9rem; color: #666; margin-bottom: 15px; }

.precos-lista { display: flex; flex-direction: column; gap: 8px; }
.preco-tag { display: flex; justify-content: space-between; background: #e8f5e9; padding: 8px 12px; border-radius: 4px; border: 1px solid #c8e6c9;}
.unidade { font-weight: bold; color: #2e7d32; }
.valor { font-weight: bold; color: #1b5e20; }
.sem-preco { font-size: 0.9rem; color: #d32f2f; font-style: italic; }
</style>