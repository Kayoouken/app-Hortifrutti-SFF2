<template>
  <div id="app">
    <!-- Barra de Navegação -->
    <nav class="navbar">
      <div class="nav-brand"> Hortifruti PDV</div>
      <div class="nav-links">
        <button 
          @click="abaAtual = 'catalogo'" 
          :class="{ active: abaAtual === 'catalogo' }">
          Catálogo de Produtos
        </button>
        <button 
          @click="abaAtual = 'expressa'" 
          :class="{ active: abaAtual === 'expressa' }">
          Planilha de Preços
        </button>
      </div>
    </nav>
    
    <!-- Área Dinâmica de Conteúdo -->
    <main class="main-content">
      <ProdutoLista v-if="abaAtual === 'catalogo'" />
      <AtualizacaoExpressa v-if="abaAtual === 'expressa'" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ProdutoLista from './components/ProdutoLista.vue'
import AtualizacaoExpressa from './components/AtualizacaoExpressa.vue'

// Estado reativo que controla qual tela está sendo exibida (inicia na nova tela para testarmos)
const abaAtual = ref('expressa')
</script>

<style>
body {
  background-color: #f4f6f8;
  margin: 0;
  font-family: Arial, sans-serif;
}

.navbar {
  background-color: #2e7d32;
  color: white;
  padding: 15px 30px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.nav-brand { font-size: 1.4rem; font-weight: bold; margin-right: 40px; }
.nav-links button {
  background: none; border: none; color: #a5d6a7; font-size: 1rem; padding: 10px 15px; cursor: pointer; border-radius: 4px; transition: 0.2s;
}
.nav-links button:hover { background-color: rgba(255,255,255,0.1); color: white; }
.nav-links button.active { background-color: rgba(255,255,255,0.2); color: white; font-weight: bold; }
.main-content {
  padding: 20px;
}
</style>