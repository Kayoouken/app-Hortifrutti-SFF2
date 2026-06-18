<template>
  <div class="container">
    <header class="header">
      <h2>Gerenciar Produtos e Preços</h2>
    </header>
    
    <!-- Busca de Produtos Existentes -->
    <div class="search-wrapper">
      <input 
        type="text" 
        v-model="termoBusca" 
        @focus="mostrarDropdown = true"
        @blur="mostrarDropdown = false"
        placeholder="🔍 Buscar produto cadastrado para alterar preços..." 
        class="input-busca"
      />
      <ul v-if="mostrarDropdown && sugestoes.length > 0" class="dropdown-sugestoes">
        <li v-for="s in sugestoes" :key="s.id" @mousedown.prevent="selecionarProduto(s)">
          <strong>#{{ s.codigo_interno }}</strong> - {{ s.nome }}
        </li>
      </ul>
    </div>

    <!-- Modo de Cadastro (quando nenhum produto está selecionado) -->
    <div class="form-card" v-if="!produtoEditando">
      <h3 style="margin-top: 0; margin-bottom: 20px;">Cadastrar Novo Produto</h3>
      <div class="form-row">
        <div class="form-group flex-2">
          <label>Nome do Produto</label>
          <input type="text" v-model="nome" placeholder="Ex: Tomate Carmem" />
        </div>
      </div>
      
      <div class="form-group">
        <label>Descrição Opcional</label>
        <textarea v-model="descricao" placeholder="Ex: Tomate de primeira linha, maduro."></textarea>
      </div>

      <div v-if="mensagem.texto" :class="['mensagem-alerta', mensagem.tipo]">
        {{ mensagem.texto }}
      </div>

      <div class="form-actions">
        <button class="btn-salvar" @click="salvar" :disabled="salvando">
          {{ salvando ? 'Salvando...' : 'Salvar Produto' }}
        </button>
      </div>
    </div>

    <!-- Tabela de Produtos Existentes -->
    <div class="produtos-lista" v-if="!produtoEditando">
      <h3>Lista de Produtos Cadastrados</h3>
      <table class="tabela-produtos">
        <thead>
          <tr>
            <th>Código</th>
            <th>Nome</th>
            <th>Descrição</th>
            <th>Preços Vinculados</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in todosProdutos" :key="p.id">
            <td class="codigo">#{{ p.codigo_interno }}</td>
            <td><strong>{{ p.nome }}</strong></td>
            <td>{{ p.descricao || '-' }}</td>
            <td>
              <div v-for="preco in p.precos" :key="preco.id" class="preco-mini-tag">
                {{ preco.unidade?.sigla || 'UN' }}: R$ {{ parseFloat(preco.preco_venda).toFixed(2).replace('.', ',') }}
              </div>
              <span v-if="!p.precos || p.precos.length === 0" class="sem-preco-mini">Nenhum</span>
            </td>
            <td>
              <div class="acoes-cell">
                <button class="btn-gear" title="Opções" @click="toggleMenu(p.id)">⚙️</button>
                <div v-if="menuAberto === p.id" class="acoes-expandidas">
                  <button class="btn-acao-mini edit" @click="selecionarProduto(p)">✏️ Editar</button>
                  <button class="btn-acao-mini del" @click="apagarProduto(p.id)">🗑️ Apagar</button>
                </div>
              </div>
            </td>
          </tr>
          <tr v-if="todosProdutos.length === 0">
            <td colspan="5" style="text-align: center; padding: 20px; color: #888;">Nenhum produto cadastrado ainda.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modo de Edição de Preços -->
    <div class="form-card" v-else>
      <div class="edit-header">
        <h3 style="margin-top:0; color:#2e7d32">Gerenciando: {{ produtoEditando.nome }} (#{{ produtoEditando.codigo_interno }})</h3>
        <button @click="limparSelecao" class="btn-cancelar">Voltar / Novo Cadastro</button>
      </div>

      <!-- Edição de Informações Básicas -->
      <div class="info-edit-box">
        <h4 class="section-title">Informações do Produto</h4>
        <div class="form-row align-end">
          <div class="form-group flex-2">
            <label>Nome do Produto</label>
            <input type="text" v-model="produtoEditando.nome" />
          </div>
          <div class="form-group flex-2">
            <label>Descrição</label>
            <input type="text" v-model="produtoEditando.descricao" />
          </div>
          <button class="btn-salvar-info" @click="salvarEdicaoInfo(produtoEditando)">💾 Salvar Alterações</button>
        </div>
      </div>

      <div class="precos-lista">
        <h4>Preços Atuais</h4>
        <div v-for="preco in produtoEditando.precos" :key="preco.id" class="preco-tag">
          <span class="unidade-badge">{{ preco.unidade?.sigla || 'UN' }}</span>
          <strong>R$ {{ parseFloat(preco.preco_venda).toFixed(2).replace('.', ',') }}</strong>
        </div>
        <p v-if="!produtoEditando.precos || produtoEditando.precos.length === 0" class="sem-preco">Nenhum preço vinculado. Adicione abaixo.</p>
      </div>

      <div class="novo-preco-box">
        <h4 class="novo-preco-title">Vincular Novo Preço</h4>
        <div class="form-row align-end">
          <div class="form-group">
            <label>Unidade</label>
            <select v-model="novoPreco.unidade_medida_id">
              <option value="" disabled>Selecione...</option>
              <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.sigla }} - {{ u.nome }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Preço de Venda (R$)</label>
            <input type="number" step="0.01" v-model="novoPreco.preco_venda" placeholder="Ex: 5.99" />
          </div>
          <button class="btn-adicionar" @click="salvarPreco">➕ Adicionar</button>
        </div>
        <div v-if="mensagemPreco.texto" :class="['mensagem-alerta', mensagemPreco.tipo]">
          {{ mensagemPreco.texto }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { criarProduto, fetchProdutos, fetchUnidades, vincularPreco } from '../api';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const nome = ref('');
const descricao = ref('');
const salvando = ref(false);
const mensagem = ref({ texto: '', tipo: '' });

const todosProdutos = ref([]);
const unidades = ref([]);
const termoBusca = ref('');
const mostrarDropdown = ref(false);
const produtoEditando = ref(null);
const menuAberto = ref(null);

const novoPreco = ref({ unidade_medida_id: '', preco_venda: '' });
const mensagemPreco = ref({ texto: '', tipo: '' });

onMounted(() => { carregarDados(); });

const carregarDados = async () => {
  todosProdutos.value = await fetchProdutos();
  let unids = await fetchUnidades();
  
  // Cria unidades básicas de forma silenciosa se o BD estiver vazio
  if (unids.length === 0) {
    try {
      await fetch(`${API_URL}/unidades/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ sigla: "KG", nome: "Quilograma" }) });
      await fetch(`${API_URL}/unidades/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ sigla: "UN", nome: "Unidade" }) });
      unids = await fetchUnidades();
    } catch(e) {}
  }
  unidades.value = unids;
};

const sugestoes = computed(() => {
  if (!termoBusca.value) return [];
  const termo = termoBusca.value.toLowerCase();
  return todosProdutos.value.filter(p => p.nome.toLowerCase().includes(termo) || p.codigo_interno.toLowerCase().includes(termo));
});

const toggleMenu = (id) => {
  menuAberto.value = menuAberto.value === id ? null : id;
};

const selecionarProduto = (produto) => {
  produtoEditando.value = produto;
  termoBusca.value = '';
  mostrarDropdown.value = false;
  mensagem.value = { texto: '', tipo: '' };
  mensagemPreco.value = { texto: '', tipo: '' };
};

const limparSelecao = () => {
  produtoEditando.value = null;
  novoPreco.value = { unidade_medida_id: '', preco_venda: '' };
};

const salvar = async () => {
  if (!nome.value) {
    mensagem.value = { texto: 'O Nome do produto é obrigatório!', tipo: 'erro' };
    return;
  }

  // Verifica se já existe um produto com nome idêntico ou muito parecido (ignorando maiúsculas/minúsculas e acentos)
  const normalizar = (str) => str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim().toLowerCase();
  const nomeFormatado = normalizar(nome.value);
  const produtoExistente = todosProdutos.value.find(p => normalizar(p.nome) === nomeFormatado);
  
  if (produtoExistente) {
    mensagem.value = { 
      texto: `Atenção: Já existe um produto cadastrado com este nome: ${produtoExistente.nome} (Código #${produtoExistente.codigo_interno}).`, 
      tipo: 'erro' 
    };
    return;
  }

  salvando.value = true;
  mensagem.value = { texto: '', tipo: '' };

  // Calcula o próximo código preenchendo as lacunas deixadas por produtos apagados
  let proximoCodigo = 1;
  if (todosProdutos.value.length > 0) {
    const codigosExistentes = todosProdutos.value
      .map(p => parseInt(p.codigo_interno))
      .filter(num => !isNaN(num))
      .sort((a, b) => a - b);
      
    for (let i = 0; i < codigosExistentes.length; i++) {
      if (codigosExistentes[i] === proximoCodigo) { proximoCodigo++; } 
      else if (codigosExistentes[i] > proximoCodigo) { break; } // Encontrou um "buraco" vazio!
    }
  }

  try {
    const prod = await criarProduto({ 
      codigo_interno: proximoCodigo.toString(), 
      nome: nome.value, 
      descricao: descricao.value || null 
    });
    nome.value = '';
    descricao.value = '';
    
    await carregarDados(); // Puxa novamente com IDs e tudo atualizado
    const produtoSalvo = todosProdutos.value.find(p => p.id === prod.id) || prod;
    if (!produtoSalvo.precos) produtoSalvo.precos = [];
    
    selecionarProduto(produtoSalvo); // Transforma em edição logo em seguida!
    
  } catch (error) {
    mensagem.value = { texto: 'Erro ao cadastrar. O código já pode existir no banco.', tipo: 'erro' };
  } finally {
    salvando.value = false;
  }
};

const apagarProduto = async (id) => {
  if (!confirm("Tem certeza que deseja apagar este produto e todos os seus preços?")) return;
  try {
    const res = await fetch(`${API_URL}/produtos/${id}`, { method: 'DELETE' });
    if (res.ok) {
      mensagem.value = { texto: 'Produto apagado com sucesso!', tipo: 'sucesso' };
      menuAberto.value = null;
      carregarDados();
    } else {
      const data = await res.json();
      alert(data.detail || 'Erro ao apagar. O produto já pode ter sido vendido.');
    }
  } catch (error) {
    alert('Erro de conexão ao tentar apagar.');
  }
};

const salvarEdicaoInfo = async (produto) => {
  try {
    const res = await fetch(`${API_URL}/produtos/${produto.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        codigo_interno: produto.codigo_interno,
        nome: produto.nome,
        descricao: produto.descricao || null
      })
    });
    if (res.ok) {
      mensagemPreco.value = { texto: 'Informações salvas com sucesso!', tipo: 'sucesso' };
      carregarDados();
    } else {
      mensagemPreco.value = { texto: 'Erro ao salvar informações.', tipo: 'erro' };
    }
  } catch (e) {
    mensagemPreco.value = { texto: 'Erro de conexão.', tipo: 'erro' };
  }
};

const salvarPreco = async () => {
  if (!novoPreco.value.unidade_medida_id || !novoPreco.value.preco_venda) {
    mensagemPreco.value = { texto: 'Preencha a unidade e o valor!', tipo: 'erro' };
    return;
  }
  try {
    const precoCriado = await vincularPreco(produtoEditando.value.id, {
      unidade_medida_id: novoPreco.value.unidade_medida_id,
      preco_venda: parseFloat(novoPreco.value.preco_venda)
    });
    mensagemPreco.value = { texto: 'Preço vinculado com sucesso!', tipo: 'sucesso' };
    
    const unidadeSelecionada = unidades.value.find(u => u.id === novoPreco.value.unidade_medida_id);
    produtoEditando.value.precos.push({ ...precoCriado, unidade: unidadeSelecionada });
    novoPreco.value.preco_venda = ''; // Limpa para digitar outro se quiser
    
    carregarDados(); // Atualiza painel geral
  } catch (error) {
    mensagemPreco.value = { texto: 'Erro. Talvez esta unidade já esteja cadastrada para este produto.', tipo: 'erro' };
  }
};
</script>

<style scoped>
.container { max-width: 1200px; margin: 0 auto; padding: 20px; font-family: sans-serif; box-sizing: border-box; }
.header { margin-bottom: 20px; }
.header h2 { margin: 0; color: #334155; }
.form-card { background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.form-row { display: flex; gap: 15px; margin-bottom: 15px; }
.form-group { display: flex; flex-direction: column; flex: 1;}
.flex-2 { flex: 2; }
.align-end { align-items: flex-end; }
.form-group label { margin-bottom: 5px; font-weight: bold; color: #555; font-size: 0.9rem; }
.form-group input, .form-group textarea, .form-group select { padding: 12px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; outline: none; background-color: #fff; color: #333; }
.form-group input:focus, .form-group textarea:focus, .form-group select:focus { border-color: #2e7d32; box-shadow: 0 0 5px rgba(46,125,50,0.2); }
.form-group textarea { resize: vertical; min-height: 80px; }
.form-actions { display: flex; justify-content: flex-end; margin-top: 10px; }
.btn-salvar { padding: 12px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; font-size: 1rem; font-weight: bold; cursor: pointer; }
.btn-salvar:hover:not(:disabled) { background-color: #388E3C; }
.btn-salvar:disabled { background-color: #9e9e9e; cursor: not-allowed; }
.btn-cancelar { padding: 8px 15px; background: #eee; color: #555; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
.mensagem-alerta { padding: 10px; margin-bottom: 15px; border-radius: 4px; font-weight: bold; text-align: center; }
.sucesso { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
.erro { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }

/* Search Transparente */
.search-wrapper { position: relative; margin-bottom: 20px; }
.input-busca { width: 100%; padding: 15px; font-size: 1.1rem; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; outline: none; background: #fff;}
.input-busca:focus { border-color: #2e7d32; box-shadow: 0 0 5px rgba(46,125,50,0.3); }
.dropdown-sugestoes { position: absolute; top: 100%; left: 0; right: 0; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(8px); border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px; list-style: none; margin: 0; padding: 0; max-height: 250px; overflow-y: auto; z-index: 1000; box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
.dropdown-sugestoes li { padding: 12px 15px; cursor: pointer; border-bottom: 1px solid #eee; color: #333; font-size: 1.05rem;}
.dropdown-sugestoes li:hover { background: rgba(46, 125, 50, 0.1); color: #2e7d32; }

/* Area de Preços */
.edit-header { display: flex; justify-content: space-between; border-bottom: 2px solid #eee; padding-bottom: 15px; margin-bottom: 15px; }
.section-title { margin-top: 0; margin-bottom: 15px; color: #444; border-bottom: 1px solid #eee; padding-bottom: 5px; }
.info-edit-box { padding: 20px; background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 20px; }
.btn-salvar-info { padding: 12px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; font-size: 1rem; font-weight: bold; cursor: pointer; height: 46px; white-space: nowrap; }
.btn-salvar-info:hover { background-color: #388E3C; }
.precos-lista { background: #fff; padding: 15px; border: 1px solid #eee; border-radius: 8px; margin-bottom: 20px;}
.preco-tag { display: flex; justify-content: space-between; background: #fafafa; border: 1px solid #eee; border-left: 4px solid #4CAF50; padding: 12px 15px; margin-bottom: 8px; border-radius: 4px; font-size: 1.1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05);}
.unidade-badge { font-weight: bold; color: #4CAF50; }
.sem-preco { color: #888; font-style: italic; }
.novo-preco-box { padding: 20px; background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; margin-top: 10px; }
.novo-preco-title { margin-top: 0; margin-bottom: 15px; color: #444; }
.btn-adicionar { padding: 12px 20px; background-color: #2196F3; color: white; border: none; border-radius: 4px; font-size: 1rem; font-weight: bold; cursor: pointer; height: 46px; display: flex; align-items: center; justify-content: center; gap: 5px; box-shadow: 0 2px 4px rgba(33,150,243,0.3); transition: background-color 0.2s; white-space: nowrap;}
.btn-adicionar:hover { background-color: #1976D2; }

/* Tabela de Produtos */
.produtos-lista { margin-top: 30px; }
.produtos-lista h3 { color: #333; margin-bottom: 15px; }
.tabela-produtos { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }
.tabela-produtos th { background: #f5f5f5; border-bottom: 2px solid #ddd; padding: 12px; text-align: left; color: #555; }
.tabela-produtos td { padding: 12px; border-bottom: 1px solid #eee; color: #333; }
.preco-mini-tag { display: inline-block; background: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 4px; font-size: 0.95rem; margin-right: 5px; margin-bottom: 5px; border: 1px solid #c8e6c9; font-weight: bold;}
.sem-preco-mini { font-size: 0.95rem; color: #999; font-style: italic; }

.acoes-cell { display: flex; align-items: center; gap: 8px; }
.btn-gear { background: none; border: none; font-size: 1.3rem; cursor: pointer; transition: transform 0.2s; padding: 2px;}
.btn-gear:hover { transform: scale(1.1); }
.acoes-expandidas { display: flex; gap: 5px; animation: fadeIn 0.2s; }
.btn-acao-mini { padding: 6px 10px; border: none; border-radius: 4px; font-size: 0.85rem; cursor: pointer; font-weight: bold; display: flex; align-items: center; gap: 4px; }
.btn-acao-mini.edit { background-color: #2196F3; color: white; }
.btn-acao-mini.edit:hover { background-color: #1976D2; }
.btn-acao-mini.del { background-color: #f44336; color: white; }
.btn-acao-mini.del:hover { background-color: #d32f2f; }
@keyframes fadeIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
</style>