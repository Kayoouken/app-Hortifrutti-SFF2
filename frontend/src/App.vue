<template>
  <div class="app-layout">
    <!-- Alerta Flutuante de Venda em Andamento -->
    <div v-if="vendaEmAndamento && telaAtual !== 'pdv'" class="popup-venda-ativa" @click="telaAtual = 'pdv'">
      <span class="popup-icone">🛒</span>
      <div class="popup-texto">
        <strong>Venda em andamento!</strong>
        <p>Clique aqui para voltar ao caixa.</p>
      </div>
    </div>

    <!-- Menu Lateral (Sidebar) -->
    <aside class="sidebar">
      
      <div class="logo">
        <h2>
          <span class="icone-logo">🛒</span>
          <span class="logo-texto">Hortifruti</span>
        </h2>
        <p class="logo-sub">Sistema Gestor (SFF2)</p>
      </div>
      <nav class="menu">
        <button 
          v-for="item in menuItems" 
          :key="item.id" 
          :class="['menu-btn', { ativo: telaAtual === item.id }]"
          @click="telaAtual = item.id"
        >
          <span class="icone">{{ item.icone }}</span>
          <span class="menu-text">{{ item.nome }}</span>
        </button>
      </nav>
      <div class="rodape-menu">
        <small class="rodape-text">v1.0.0 - Dev Mode</small>
      </div>
    </aside>

    <!-- Área de Conteúdo Principal -->
    <main class="main-content">
      <!-- A Nova Venda usa v-show para não ser apagada e perder os dados ao mudar de tela -->
      <NovaVenda v-show="telaAtual === 'pdv'" :ativa="telaAtual === 'pdv'" @venda-ativa="vendaEmAndamento = $event" />
      <HistoricoVendas v-if="telaAtual === 'historico'" />
      <CadastroCliente v-if="telaAtual === 'clientes'" />
      
      <CadastroProduto v-if="telaAtual === 'produtos'" />
      <AtualizacaoExpressa v-if="telaAtual === 'precos'" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Importando os componentes que já criamos
import NovaVenda from './components/NovaVenda.vue';
import CadastroCliente from './components/CadastroCliente.vue';
import CadastroProduto from './components/CadastroProduto.vue';
import HistoricoVendas from './components/HistoricoVendas.vue';
import AtualizacaoExpressa from './components/AtualizacaoExpressa.vue';

// Define qual tela será aberta por padrão (pdv)
const telaAtual = ref('pdv');
const vendaEmAndamento = ref(false);

// Lista de itens do menu
const menuItems = [
  { id: 'pdv', nome: 'Frente de Caixa (PDV)', icone: '🏷️' },
  { id: 'historico', nome: 'Histórico de Vendas', icone: '📜' },
  { id: 'clientes', nome: 'Gestão de Clientes', icone: '👥' },
  { id: 'produtos', nome: 'Catálogo de Produtos', icone: '📦' },
  { id: 'precos', nome: 'Atualização Expressa', icone: '⚡' }
];
</script>

<style>
/* Estilo global para resetar margens da página */
body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f4f6f8;
  font-size: 22px;
}

#app {
  max-width: 100% !important;
  width: 100%;
  padding: 0 !important;
  margin: 0 !important;
}

.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Estilos do Menu Lateral */
.sidebar { 
  width: 90px; 
  background-color: #1b5e20; 
  color: white; 
  display: flex; 
  flex-direction: column; 
  box-shadow: 2px 0 5px rgba(0,0,0,0.1); 
  z-index: 10; 
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
  white-space: nowrap; 
  overflow-x: hidden; 
}
.sidebar:hover { width: 380px; }

.logo { padding: 25px 25px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; }
.logo h2 { margin: 0; font-size: 2.2rem; color: #fff; display: flex; align-items: center; gap: 15px; }
.icone-logo { font-size: 2.2rem; min-width: 35px; text-align: center; }
.logo-texto { opacity: 0; transition: opacity 0.1s ease; }
.sidebar:hover .logo-texto { opacity: 1; transition: opacity 0.3s ease 0.1s; }
.logo-sub { margin: 5px 0 0 50px; font-size: 1.1rem; color: #a5d6a7; opacity: 0; transition: opacity 0.1s ease; }
.sidebar:hover .logo-sub { opacity: 1; transition: opacity 0.3s ease 0.1s; }

.menu { display: flex; flex-direction: column; padding: 20px 0; flex: 1; }
.menu-btn { background: none; border: none; color: #e8f5e9; padding: 22px 25px; text-align: left; font-size: 1.25rem; cursor: pointer; transition: background-color 0.2s, color 0.2s; display: flex; align-items: center; gap: 15px; width: 100%; box-sizing: border-box; }
.menu-btn:not(.ativo) { border-left: 5px solid transparent; } /* Evita que o icone pule quando ganha a borda verde de ativo */
.menu-btn:hover { background-color: rgba(255,255,255,0.1); color: #fff; }
.menu-btn.ativo { background-color: #2e7d32; border-left: 5px solid #69f0ae; color: #fff; font-weight: bold; }
.icone { font-size: 1.6rem; min-width: 35px; text-align: center; flex-shrink: 0; }
.menu-text { opacity: 0; transition: opacity 0.1s ease; }
.sidebar:hover .menu-text { opacity: 1; transition: opacity 0.3s ease 0.1s; }

.rodape-menu { padding: 15px; text-align: center; color: #81c784; border-top: 1px solid rgba(255,255,255,0.1); }
.rodape-text { opacity: 0; transition: opacity 0.1s ease; }
.sidebar:hover .rodape-text { opacity: 1; transition: opacity 0.3s ease 0.1s; }

/* Estilos da Área Principal */
.main-content {
  flex: 1;
  overflow-y: auto; /* Permite rolar a tela se o conteúdo for longo */
  padding: 15px;
  background-color: #f4f6f8;
}

.em-construcao { text-align: center; padding: 50px; color: #666; }
.em-construcao h2 { color: #2e7d32; }

/* Estilos do Popup de Venda Ativa */
.popup-venda-ativa {
  position: fixed;
  top: 20px;
  right: 25px;
  background-color: #ff9800;
  color: #fff;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  gap: 15px;
  cursor: pointer;
  z-index: 9999;
  animation: slideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.popup-venda-ativa:hover { background-color: #f57c00; transform: scale(1.02); transition: all 0.2s; }
.popup-icone { font-size: 2.2rem; }
.popup-texto strong { display: block; font-size: 1.1rem; margin-bottom: 2px; }
.popup-texto p { margin: 0; font-size: 0.95rem; opacity: 0.95; }

@keyframes slideIn { from { transform: translateX(120%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
</style>