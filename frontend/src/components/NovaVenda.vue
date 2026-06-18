<template>
  <div class="container">
    <header class="header">
      <h2>Frente de Caixa (PDV) - Nova Nota</h2>
    </header>
    
    <!-- ETAPA 1: Identificação do Cliente -->
    <div v-if="!clienteConfirmado" class="painel-cliente">
      <h3>1. Identificação do Cliente</h3>
      <div class="form-grid">
        <div class="form-group" style="position: relative;">
          <label>Nome do Cliente *</label>
          <input 
            type="text" 
            v-model="cliente.nome" 
            @focus="mostrarDropdownCliente = true"
            @blur="esconderDropdownClienteAtrasado"
            placeholder="Ex: João da Silva" 
            class="input-form" 
          />
          <ul v-if="mostrarDropdownCliente && sugestoesCliente.length > 0" class="dropdown-sugestoes">
            <li v-for="c in sugestoesCliente" :key="c.id" @mousedown.prevent="selecionarCliente(c)">
              <strong>{{ c.nome }}</strong> <span v-if="c.cpf_cnpj">- Doc: {{ c.cpf_cnpj }}</span>
            </li>
          </ul>
        </div>
        <div class="form-group">
          <label>CPF / CNPJ (Opcional)</label>
          <input type="text" v-model="cliente.cpf_cnpj" placeholder="Apenas números" class="input-form" />
        </div>
        <div class="form-group">
          <label>Telefone (Opcional)</label>
          <input type="text" v-model="cliente.telefone" placeholder="(00) 00000-0000" class="input-form" />
        </div>
      </div>
      <div class="acoes-cliente">
        <button class="btn-primario" @click="confirmarCliente">Iniciar Venda ➔</button>
        <button class="btn-secundario" @click="pularCliente">Vender sem identificar (Consumidor Final)</button>
      </div>
    </div>
      
    <!-- ETAPA 2: Carrinho de Compras -->
    <div v-else class="pdv-container">
      <div class="cabecalho-nota">
        <div class="info-nota">
          <h3>Nota em emissão para: <span class="destaque-cliente">{{ cliente.nome || 'Consumidor Final' }}</span></h3>
          <p v-if="cliente.cpf_cnpj" class="doc-cliente">Documento: {{ cliente.cpf_cnpj }}</p>
        </div>
        <button class="btn-secundario mini" @click="clienteConfirmado = false">✎ Alterar Cliente</button>
      </div>

      <div class="pdv-grid">
        <div class="painel-produtos">
          <div class="busca-wrapper">
            <span class="icone-busca">🔍</span>
            <input 
              type="text" 
              v-model="termoBusca"
              @focus="mostrarDropdown = true"
              @blur="esconderDropdownAtrasado"
              @keyup.enter="selecionarPrimeiraSugestao"
              placeholder="Buscar por código ou nome do produto... (Ex: 101, Tomate)" 
              class="input-busca" 
            />
            <ul v-if="mostrarDropdown && sugestoes.length > 0" class="dropdown-sugestoes">
              <li v-for="s in sugestoes" :key="s.id" @mousedown.prevent="selecionarProduto(s)">
                <strong>#{{ s.codigo_interno }}</strong> - {{ s.nome }}
              </li>
            </ul>
          </div>
          <div class="carrinho">
            <table class="tabela-carrinho">
              <thead>
                <tr>
                  <th class="text-center">#</th>
                  <th>Código</th>
                  <th>Produto</th>
                  <th>Qtd.</th>
                  <th>Unidade</th>
                  <th>Preço Unit.</th>
                  <th class="text-right">Subtotal</th>
                  <th>Ação</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in carrinho" :key="index">
                  <td class="text-center index-item">{{ index + 1 }}</td>
                  <td class="codigo-produto">{{ item.produto.codigo_interno }}</td>
                  <td class="nome-produto">{{ item.produto.nome }}</td>
                  <td>
                    <input type="number" step="any" min="0.001" v-model.number="item.quantidade" class="input-mini" />
                  </td>
                  <td>
                    <select v-model="item.unidade_medida_id" @change="atualizarPreco(item)" class="input-mini-select">
                      <option v-for="u in unidades" :key="u.id" :value="u.id">
                        {{ u.sigla }}
                      </option>
                    </select>
                  </td>
                  <td>
                    <div class="preco-wrapper">
                      R$ <input type="number" step="any" min="0" v-model.number="item.preco_unitario" class="input-preco" />
                    </div>
                  </td>
                  <td class="subtotal-cell text-right">R$ {{ (item.quantidade * item.preco_unitario).toFixed(2).replace('.', ',') }}</td>
                  <td class="text-center"><button @click="removerItem(index)" class="btn-remover" title="Remover Item">🗑️</button></td>
                </tr>
                <tr v-if="carrinho.length === 0">
                  <td colspan="8" class="placeholder-cell">
                    <p class="placeholder-text">Sua nota está vazia. Busque um produto para iniciar.</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <div class="painel-resumo">
          <h3>Resumo da Nota</h3>
          <div class="total-box">
            <span>Total:</span>
            <span class="valor-total">R$ {{ totalVenda.toFixed(2).replace('.', ',') }}</span>
          </div>
          <div v-if="mensagem.texto" :class="['mensagem-alerta', mensagem.tipo]">
            {{ mensagem.texto }}
          </div>
          <button class="btn-finalizar" @click="finalizar" :disabled="processando || carrinho.length === 0">
            {{ processando ? '⏳ Processando...' : '✔ Finalizar Venda' }}
          </button>
          <button class="btn-cancelar-venda" @click="cancelarVenda" :disabled="processando">
            Cancelar Venda
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { fetchProdutos } from '../api';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const emit = defineEmits(['venda-ativa']);
const props = defineProps({ ativa: Boolean });

const termoBusca = ref('');
const mostrarDropdown = ref(false);
const todosProdutos = ref([]);
const produtoSelecionado = ref(null);
const carrinho = ref([]);
const processando = ref(false);
const mensagem = ref({ texto: '', tipo: '' });
const unidades = ref([]);
const cliente = ref({ id: null, nome: '', cpf_cnpj: '', telefone: '' });
const clienteConfirmado = ref(false);
const todosClientes = ref([]);
const mostrarDropdownCliente = ref(false);

onMounted(async () => {
  todosProdutos.value = await fetchProdutos();
  try {
    const res = await fetch(`${API_URL}/unidades/`);
    if (res.ok) {
      let unids = await res.json();
      
      // Garante que as opções padrão existem no banco de dados
      const unidadesPadrao = [
        { sigla: "KG", nome: "Quilograma" },
        { sigla: "CX", nome: "Caixa" },
        { sigla: "UND", nome: "Unidade" },
        { sigla: "SACO", nome: "Saco" }
      ];
      
      let precisaAtualizar = false;
      for (let up of unidadesPadrao) {
        if (!unids.find(u => u.sigla === up.sigla)) {
          await fetch(`${API_URL}/unidades/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(up) });
          precisaAtualizar = true;
        }
      }
      
      if (precisaAtualizar) {
        const resNova = await fetch(`${API_URL}/unidades/`);
        unids = await resNova.json();
      }
      
      unidades.value = unids;
    }
  } catch(e) { console.error("Erro ao carregar unidades", e); }

  try {
    const resCli = await fetch(`${API_URL}/clientes/`);
    if (resCli.ok) {
      todosClientes.value = await resCli.json();
    }
  } catch(e) { console.error("Erro ao carregar clientes", e); }
});

// SOLUÇÃO RAIZ: Atualiza as listas sempre que o usuário voltar para a aba de Nova Venda
watch(() => props.ativa, async (isAtiva) => {
  if (isAtiva) {
    todosProdutos.value = await fetchProdutos(); // Puxa produtos novos que foram recém cadastrados
    try {
      const resCli = await fetch(`${API_URL}/clientes/`);
      if (resCli.ok) todosClientes.value = await resCli.json(); // Puxa novos clientes
    } catch(e) {}
    try {
      const resUni = await fetch(`${API_URL}/unidades/`);
      if (resUni.ok) unidades.value = await resUni.json(); // Puxa novas unidades
    } catch(e) {}
  }
});

// Monitora se há uma venda em andamento para avisar o App.vue
const isVendaAtiva = computed(() => clienteConfirmado.value || carrinho.value.length > 0);
watch(isVendaAtiva, (novoValor) => {
  emit('venda-ativa', novoValor);
}, { immediate: true });

const sugestoes = computed(() => {
  if (!termoBusca.value) return [];
  const termo = termoBusca.value.toLowerCase();
  return todosProdutos.value.filter(p => 
    p.nome.toLowerCase().includes(termo) || 
    p.codigo_interno.toLowerCase().includes(termo)
  );
});

const sugestoesCliente = computed(() => {
  if (!cliente.value.nome) return [];
  const termo = cliente.value.nome.toLowerCase();
  return todosClientes.value.filter(c => 
    c.nome.toLowerCase().includes(termo) || 
    (c.cpf_cnpj && c.cpf_cnpj.includes(termo))
  );
});

const esconderDropdownClienteAtrasado = () => {
  setTimeout(() => { mostrarDropdownCliente.value = false; }, 200);
};

const selecionarCliente = (c) => {
  cliente.value = { id: c.id, nome: c.nome, cpf_cnpj: c.cpf_cnpj || '', telefone: c.telefone || '' };
  mostrarDropdownCliente.value = false;
};

const confirmarCliente = async () => {
  if (!cliente.value.nome) {
    alert("Preencha o nome do cliente ou escolha vender sem identificar.");
    return;
  }
  
  if (cliente.value.id) {
    clienteConfirmado.value = true;
    return; // Cliente já existe e foi selecionado da lista, podemos prosseguir direto!
  }

  // Se o usuário apenas digitou o nome (sem clicar na lista), verifica se já existe na base
  const clienteExistente = todosClientes.value.find(c => c.nome.toLowerCase() === cliente.value.nome.toLowerCase().trim());
  if (clienteExistente) {
    cliente.value.id = clienteExistente.id;
    clienteConfirmado.value = true;
    return;
  }

  // Tenta registrar silenciosamente o cliente no backend para guardar o histórico
  try {
    const res = await fetch(`${API_URL}/clientes/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nome: cliente.value.nome,
        cpf_cnpj: cliente.value.cpf_cnpj || null, // null evita erro de CPF vazio duplicado
        telefone: cliente.value.telefone || null
      })
    });
    
    if (res.ok) {
      const data = await res.json();
      cliente.value.id = data.id; // Vincula o ID real para a venda
    }
  } catch (e) {
    console.log("Aviso: Cliente já existe ou erro na API", e);
  }

  clienteConfirmado.value = true;
};

const pularCliente = () => {
  cliente.value = { id: null, nome: 'Consumidor Final', cpf_cnpj: '', telefone: '' };
  clienteConfirmado.value = true;
};

const esconderDropdownAtrasado = () => {
  setTimeout(() => { mostrarDropdown.value = false; }, 200);
};

const selecionarPrimeiraSugestao = () => {
  if (sugestoes.value.length > 0) {
    selecionarProduto(sugestoes.value[0]);
  }
};

const selecionarProduto = (produto) => {
  produtoSelecionado.value = produto;
  termoBusca.value = ''; // Limpa a busca ao selecionar
  // Verifica se o produto já existe no carrinho
  const itemExistente = carrinho.value.find(i => i.produto.id === produto.id);
  
  if (itemExistente) {
    // Se já existe, apenas soma a quantidade
    itemExistente.quantidade++;
  } else {
    // Pega o primeiro preço cadastrado no produto como padrão
    let precoPadrao = 0;
    let unidadeIdPadrao = unidades.value.length > 0 ? unidades.value[0].id : 1;

    if (produto.precos && produto.precos.length > 0) {
      precoPadrao = parseFloat(produto.precos[0].preco_venda);
      // Usa a chave estrangeira direta (unidade_medida_id) para evitar falhas se o objeto aninhado 'unidade' não for carregado
      unidadeIdPadrao = produto.precos[0].unidade_medida_id || (produto.precos[0].unidade && produto.precos[0].unidade.id) || unidadeIdPadrao;
    }

    // Adiciona o novo item
    carrinho.value.push({
      produto: produto,
      unidade_medida_id: unidadeIdPadrao,
      quantidade: 1,
      preco_unitario: precoPadrao
    });
  }

  termoBusca.value = '';
  mostrarDropdown.value = false;
  mensagem.value = { texto: '', tipo: '' };
};

const atualizarPreco = (item) => {
  // (item.produto.precos || []) impede o sistema de quebrar caso o produto não tenha preços cadastrados
  const precoEncontrado = (item.produto.precos || []).find(p => p.unidade_medida_id === item.unidade_medida_id);
  if (precoEncontrado) {
    item.preco_unitario = parseFloat(precoEncontrado.preco_venda);
  }
};

const removerItem = (index) => {
  carrinho.value.splice(index, 1);
};

// Soma dinamicamente (Quantidade * Preço Específico) de todos os itens
const totalVenda = computed(() => {
  // O parseFloat previne erros (NaN) caso o operador apague tudo de dentro do input de quantidade
  return carrinho.value.reduce((total, item) => {
    const qtd = parseFloat(item.quantidade) || 0;
    const preco = parseFloat(item.preco_unitario) || 0;
    return total + parseFloat((qtd * preco).toFixed(2));
  }, 0);
});

const registrarVendaAPI = async (payload) => {
  const response = await fetch(`${API_URL}/vendas/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const errorData = await response.json();
    let errorMsg = 'Erro ao registrar venda';
    if (errorData.detail) {
      if (typeof errorData.detail === 'string') {
        errorMsg = errorData.detail; // Erro em texto gerado manualmente pela API
      } else if (Array.isArray(errorData.detail)) {
        // Erro de Validação Pydantic/FastAPI (Erro 422 - Campos inválidos)
        errorMsg = errorData.detail.map(e => `Campo '${e.loc[e.loc.length - 1]}': ${e.msg}`).join(' | ');
      } else {
        errorMsg = JSON.stringify(errorData.detail);
      }
    }
    throw new Error(errorMsg);
  }
  return response.json();
};

const cancelarVenda = () => {
  if (confirm("Tem certeza que deseja cancelar a compra ?")) {
    carrinho.value = [];
    cliente.value = { id: null, nome: '', cpf_cnpj: '', telefone: '' };
    clienteConfirmado.value = false;
    mensagem.value = { texto: '', tipo: '' };
  }
};

const finalizar = async () => {
  if (carrinho.value.length === 0) return;
  processando.value = true;
  mensagem.value = { texto: '', tipo: '' };

  // Impede o envio de campos em branco ou zerados (NaN), o que costuma gerar o erro 422 no FastAPI
  const carrinhoInvalido = carrinho.value.some(item => 
    isNaN(parseFloat(item.quantidade)) || isNaN(parseFloat(item.preco_unitario))
  );
  if (carrinhoInvalido) {
    mensagem.value = { texto: 'Existem itens com quantidade ou preço em branco/inválidos.', tipo: 'erro' };
    processando.value = false;
    return;
  }

  const payload = {
    cliente_id: cliente.value.id || null,
    valor_total: parseFloat(totalVenda.value.toFixed(2)),
    itens: carrinho.value.map(item => ({
      produto_id: item.produto.id,
      unidade_medida_id: item.unidade_medida_id,
      quantidade: parseFloat(item.quantidade),
      preco_unitario_aplicado: parseFloat(item.preco_unitario),
      subtotal: parseFloat((item.quantidade * item.preco_unitario).toFixed(2))
    }))
  };

  try {
    await registrarVendaAPI(payload);
    mensagem.value = { texto: '✔ Venda registrada com sucesso!', tipo: 'sucesso' };
    setTimeout(() => {
      todosClientes.value.push({...cliente.value}); // Adiciona localmente para futuras buscas
      carrinho.value = []; // Limpa o carrinho
      cliente.value = { id: null, nome: '', cpf_cnpj: '', telefone: '' }; // Reseta o cliente
      clienteConfirmado.value = false; // Volta para a Etapa 1
    }, 2000); // Aguarda 2 segundos para mostrar o sucesso e reinicia
  } catch (error) {
    mensagem.value = { texto: error.message, tipo: 'erro' };
  } finally {
    processando.value = false;
  }
};
</script>

<style scoped>
.container { max-width: 1400px; margin: 0 auto; padding: 20px; font-family: sans-serif; box-sizing: border-box; }
.header { margin-bottom: 20px; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; }
.header h2 { margin: 0; color: #333; }

/* Estilos da Etapa 1 (Cliente) */
.painel-cliente { background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
.painel-cliente h3 { margin-top: 0; color: #2e7d32; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }
.form-grid { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 15px; margin-bottom: 20px; }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-weight: bold; color: #555; font-size: 0.9rem; }
.input-form { padding: 12px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; outline: none; background-color: #fff; color: #333; }
.input-form:focus { border-color: #2e7d32; box-shadow: 0 0 5px rgba(46,125,50,0.2); }
.acoes-cliente { display: flex; gap: 10px; flex-wrap: wrap; }
.btn-primario { padding: 12px 20px; background-color: #2e7d32; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 1rem;}
.btn-primario:hover { background-color: #1b5e20; }
.btn-secundario { padding: 12px 20px; background-color: #f5f5f5; color: #333; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 1rem;}
.btn-secundario:hover { background-color: #e0e0e0; }
.btn-secundario.mini { padding: 8px 12px; font-size: 0.9rem; }

.pdv-grid { display: grid; grid-template-columns: 2.4fr 1fr; gap: 20px; align-items: start; }
.painel-produtos { min-width: 0; background: #fff; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
.painel-resumo { position: sticky; top: 0; gap: 20px; background: #fff; padding: 25px; border-radius: 10px; border: none; border-top: 6px solid #2e7d32; box-shadow: 0 4px 20px rgba(0,0,0,0.08); display: flex; flex-direction: column; justify-content: space-between; z-index: 5; }
.painel-resumo h3 { margin-top: 0; color: #333; font-size: 1.4rem; border-bottom: 2px solid #eee; padding-bottom: 15px; }

.busca-wrapper { position: relative; margin-bottom: 25px; }
.icone-busca { position: absolute; left: 18px; top: 50%; transform: translateY(-50%); font-size: 1.4rem; color: #888; pointer-events: none; }
.input-busca { width: 100%; padding: 18px 20px 18px 55px; font-size: 1.2rem; border: 2px solid #e0e0e0; border-radius: 10px; outline: none; box-sizing: border-box; background: #fff; color: #333; transition: all 0.3s ease; }
.input-busca:focus { border-color: #2e7d32; box-shadow: 0 4px 15px rgba(46,125,50,0.1); }

/* Cabeçalho da Nota Fixado */
.cabecalho-nota { display: flex; justify-content: space-between; align-items: center; background: #e8f5e9; padding: 15px 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
.info-nota h3 { margin: 0; color: #333; font-size: 1.2rem; }
.destaque-cliente { color: #2e7d32; font-weight: 900; }
.doc-cliente { margin: 5px 0 0 0; color: #666; font-size: 0.95rem; }

/* Estilo do Dropdown */
.dropdown-sugestoes { 
  position: absolute; top: 100%; left: 0; right: 0; 
  background: rgba(255, 255, 255, 0.95); 
  backdrop-filter: blur(8px);
  border: 1px solid #ddd; border-top: none; 
  border-radius: 0 0 8px 8px; 
  list-style: none; margin: 0; padding: 0; 
  max-height: 250px; overflow-y: auto; z-index: 1000;
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}
.dropdown-sugestoes li { padding: 12px 15px; cursor: pointer; border-bottom: 1px solid #eee; color: #333; font-size: 1.05rem;}
.dropdown-sugestoes li:hover { background: rgba(46, 125, 50, 0.1); color: #2e7d32; }

.carrinho { min-height: 350px; background: #fafafa; border: 1px solid #eee; border-radius: 10px; display: flex; flex-direction: column; padding: 15px; overflow-x: auto;}
.placeholder-cell { border-bottom: none !important; }
.placeholder-text { color: #888; font-style: italic; text-align: center; padding: 80px 0; margin: 0; }
.produto-selecionado { text-align: center; color: #2e7d32; }

/* Estilos da Tabela do Carrinho */
.tabela-carrinho { width: 100%; text-align: left; }
.tabela-carrinho th { background-color: #eceff1; border-bottom: 2px solid #cfd8dc; padding: 12px 10px; color: #37474f; font-weight: bold; white-space: nowrap; }
.tabela-carrinho td { padding: 15px 10px; border-bottom: 1px solid #eee; vertical-align: middle; }
.tabela-carrinho tbody tr:nth-child(even) { background-color: #f9f9f9; }
.tabela-carrinho tbody tr:hover { background-color: #f5f5f5; }
.codigo-produto { font-family: monospace; color: #888; font-size: 1.05rem; }
.nome-produto { font-weight: bold; color: #333; }
.text-truncate { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.index-item { font-weight: bold; color: #555; font-size: 0.95rem; width: 30px; }

/* Inputs minimalistas dentro da tabela */
.qtd-valor-wrapper { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.multiplicador { color: #555; font-weight: bold; font-size: 0.9rem; white-space: nowrap; }
.preco-wrapper { display: flex; align-items: center; gap: 5px; white-space: nowrap; }
.input-mini { width: 60px; padding: 6px; border: 1px solid #c8e6c9; background: #f1f8e9; border-radius: 6px; outline: none; text-align: right; font-size: 0.95rem; transition: all 0.2s; color: #2e7d32; font-weight: 500; }
.input-mini:focus { border-color: #4CAF50; background: #fff; box-shadow: 0 0 5px rgba(76,175,80,0.2); color: #333; }
.input-mini-select { width: 65px; padding: 6px; border: 1px solid #c8e6c9; background: #f1f8e9; border-radius: 6px; outline: none; color: #2e7d32; text-align: center; cursor: pointer; transition: all 0.2s; font-weight: 500; }
.input-mini-select:focus, .input-mini-select:hover { border-color: #4CAF50; background: #fff; box-shadow: 0 0 5px rgba(76,175,80,0.2); color: #333; }
.input-mini-select option { color: #333; background: #fff; padding: 5px; }
.input-preco { width: 75px; padding: 6px; border: 1px solid #c8e6c9; background: #f1f8e9; border-radius: 6px; outline: none; text-align: right; font-size: 0.95rem; transition: all 0.2s; color: #2e7d32; font-weight: 500; }
.input-preco:focus { border-color: #4CAF50; background: #fff; box-shadow: 0 0 5px rgba(76,175,80,0.2); color: #333; }

.subtotal-cell { font-weight: bold; color: #2e7d32; white-space: nowrap; min-width: 90px; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.btn-remover { background: transparent; border: none; padding: 5px; font-size: 1.3rem; cursor: pointer; transition: transform 0.2s; display: inline-flex; align-items: center; justify-content: center; }
.btn-remover:hover { transform: scale(1.2); }

.total-box { margin: 15px 0 25px 0; background: #f1f8e9; padding: 20px; border-radius: 8px; border: 1px solid #c8e6c9; display: flex; justify-content: space-between; align-items: center; font-size: 1.4rem; font-weight: bold; color: #333; }
.valor-total { color: #2e7d32; font-size: 2.4rem; }
.btn-finalizar { padding: 15px; background-color: #2e7d32; color: white; border: none; border-radius: 4px; font-size: 1.1rem; font-weight: bold; cursor: pointer; width: 100%; transition: background-color 0.2s; }
.btn-finalizar:hover:not(:disabled) { background-color: #1b5e20; }
.btn-finalizar:disabled { background-color: #a5d6a7; cursor: not-allowed; }
.btn-cancelar-venda { padding: 15px; background-color: transparent; color: #f44336; border: 2px solid #f44336; border-radius: 4px; font-size: 1.1rem; font-weight: bold; cursor: pointer; width: 100%; margin-top: 10px; transition: all 0.2s; }
.btn-cancelar-venda:hover:not(:disabled) { background-color: #ffebee; }
.btn-cancelar-venda:disabled { opacity: 0.5; cursor: not-allowed; }

/* Mensagens */
.mensagem-alerta { padding: 12px; margin-bottom: 15px; border-radius: 4px; font-weight: bold; text-align: center; font-size: 0.95rem; }
.sucesso { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
.erro { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }

/* Animação de Feedback Visual (Piscar) */
@keyframes piscarVerdeAnim {
  0% { background-color: #c8e6c9; transform: scale(1.005); }
  50% { background-color: #a5d6a7; transform: scale(1.005); }
  100% { background-color: transparent; transform: scale(1); }
}
.piscar-verde { animation: piscarVerdeAnim 0.5s ease-out; }
</style>