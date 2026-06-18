<template>
  <div class="container">
    <header class="header">
      <h2>Histórico de Notas (Vendas)</h2>
    </header>

    <!-- Barra de Filtros -->
    <div class="filtros-bar">
      <div class="filtro-grupo flex-grow search-wrapper">
        <input 
          type="text" 
          v-model="filtros.busca" 
          placeholder="Buscar por ID ou Cliente..." 
          class="input-filtro"
          @focus="mostrarDropdownBusca = true"
          @blur="esconderDropdownAtrasado"
          @keyup.enter="buscarHistorico"
        />
        <ul v-if="mostrarDropdownBusca && sugestoesBusca.length > 0" class="dropdown-sugestoes">
          <li v-for="s in sugestoesBusca" :key="s.tipo + s.id" @mousedown.prevent="selecionarSugestao(s)">
            <span v-if="s.tipo === 'cliente'">👤 <strong>{{ s.nome }}</strong> (Cliente)</span>
            <span v-if="s.tipo === 'venda'">🧾 Venda <strong>#{{ s.id }}</strong> - {{ s.cliente_nome }}</span>
          </li>
        </ul>
      </div>
      <div class="filtro-grupo">
        <input type="date" v-model="filtros.data" class="input-filtro" />
      </div>
      <div class="filtro-grupo">
        <select v-model="filtros.status" class="input-filtro">
          <option value="Todas">Todas</option>
          <option value="Concluídas">Concluídas</option>
          <option value="Canceladas">Canceladas</option>
        </select>
      </div>
      <div class="filtro-grupo btn-direita">
        <button class="btn-buscar" @click="buscarHistorico">Atualizar Dados</button>
      </div>
    </div>

    <div class="card">
      <div v-if="carregando" class="loading">Carregando histórico...</div>
      
      <table class="table" v-else>
        <thead>
          <tr>
            <th class="text-center col-id">ID</th>
            <th class="text-center">Data / Hora</th>
            <th class="text-left">Cliente</th>
            <th class="text-center">Qtd. Itens Diferentes</th>
            <th class="text-right">Valor Total</th>
            <th class="text-center col-acoes">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="venda in vendasExibidas" :key="venda.id" @click="abrirDetalhes(venda)" class="linha-clicavel">
            <td class="codigo text-center">#{{ venda.id }}</td>
            <td class="text-center">{{ formatarData(venda.data_venda) }}</td>
            <td class="text-left"><strong>{{ getNomeCliente(venda) }}</strong></td>
            <td class="text-center">{{ venda.itens ? venda.itens.length : 0 }} itens</td>
            <td class="valor-total text-right">R$ {{ parseFloat(venda.valor_total).toFixed(2).replace('.', ',') }}</td>
            <td class="text-center">
              <button class="btn-acao edit" @click.stop="abrirParaEdicao(venda)" title="Editar Venda">✏️ Editar</button>
              <button class="btn-acao print" @click.stop="imprimirRecibo(venda)" title="Imprimir Recibo">🖨️ Imprimir</button>
              <button class="btn-acao del" @click.stop="apagarVenda(venda.id)" title="Cancelar Venda">🗑️ Cancelar</button>
            </td>
          </tr>
          <tr v-if="vendasExibidas.length === 0">
            <td colspan="6" class="empty-state">Nenhuma venda registrada ainda.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal de Detalhes da Venda -->
    <div v-if="vendaSelecionada" class="modal-overlay" @click.self="fecharDetalhes">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Detalhes da Venda #{{ vendaSelecionada.id }}</h3>
          <button class="btn-fechar-icon" @click="fecharDetalhes">✖</button>
        </div>
        <div class="modal-body">
          <div class="info-resumo">
            <p><strong>Cliente:</strong> {{ getNomeCliente(vendaSelecionada) }}</p>
            <p><strong>Data:</strong> {{ formatarData(vendaSelecionada.data_venda) }}</p>
            <p><strong>Total:</strong> <span class="valor-total">R$ {{ parseFloat(vendaSelecionada.valor_total).toFixed(2).replace('.', ',') }}</span></p>
          </div>

          <div v-if="!editando">
            <h4>Itens da Venda</h4>
            <table class="table-itens">
              <thead>
                <tr>
                  <th>Produto</th>
                  <th class="text-center">Qtd</th>
                  <th class="text-right">V. Unitário</th>
                  <th class="text-right">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in vendaSelecionada.itens" :key="item.id">
                  <td>{{ getNomeProduto(item.produto_id) }}</td>
                  <td class="text-center">{{ parseFloat(item.quantidade).toString() }} {{ getSiglaUnidade(item.unidade_medida_id) }}</td>
                  <td class="text-right">R$ {{ parseFloat(item.preco_unitario_aplicado).toFixed(2).replace('.', ',') }}</td>
                  <td class="text-right"><strong>R$ {{ parseFloat(item.subtotal).toFixed(2).replace('.', ',') }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <h4>Editando Itens da Nota</h4>
              <h3 style="color: #2e7d32; margin: 0;">Novo Total: R$ {{ totalEdicao.toFixed(2).replace('.', ',') }}</h3>
            </div>
            
            <table class="table-itens edit-table">
              <thead>
                <tr>
                  <th>Produto</th>
                  <th class="text-center">Qtd</th>
                  <th class="text-center">Unidade</th>
                  <th class="text-right">V. Unitário</th>
                  <th class="text-right">Subtotal</th>
                  <th class="text-center">Ação</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in carrinhoEdicao" :key="idx">
                  <td>{{ item.produto.nome }}</td>
                  <td class="text-center">
                    <input type="number" step="any" min="0.001" v-model.number="item.quantidade" class="input-mini" />
                  </td>
                  <td class="text-center">
                    <select v-model="item.unidade_medida_id" @change="atualizarPrecoEdicao(item)" class="input-mini-select">
                      <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.sigla }}</option>
                    </select>
                  </td>
                  <td class="text-right">
                    <div style="display:inline-flex; align-items:center; gap:4px; justify-content:flex-end; width:100%;">
                      R$ <input type="number" step="any" min="0" v-model.number="item.preco_unitario_aplicado" class="input-preco" />
                    </div>
                  </td>
                  <td class="text-right" style="white-space: nowrap;">R$ {{ (item.quantidade * item.preco_unitario_aplicado).toFixed(2).replace('.', ',') }}</td>
                  <td class="text-center">
                    <button @click="removerItemEdicao(idx)" class="btn-remover" title="Remover Item">🗑️</button>
                  </td>
                </tr>
                <tr v-if="carrinhoEdicao.length === 0">
                  <td colspan="6" style="text-align: center; color: #888; padding: 20px;">A nota está vazia. Adicione um produto abaixo.</td>
                </tr>
              </tbody>
            </table>
            
            <div class="busca-edicao-wrapper">
              <input 
                type="text" 
                v-model="termoBuscaProduto"
                @focus="mostrarDropdownProduto = true"
                @blur="esconderDropdownProdutoAtrasado"
                placeholder="🔍 Buscar produto para adicionar à nota..." 
                class="input-busca-edicao" 
              />
              <ul v-if="mostrarDropdownProduto && sugestoesProduto.length > 0" class="dropdown-sugestoes" style="top: 100%;">
                <li v-for="s in sugestoesProduto" :key="s.id" @mousedown.prevent="adicionarProdutoEdicao(s)">
                  <strong>#{{ s.codigo_interno }}</strong> - {{ s.nome }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="modal-footer" v-if="!editando">
          <button class="btn-acao edit" @click="iniciarEdicao">✏️ Editar Venda</button>
          <button class="btn-acao print" @click="imprimirRecibo(vendaSelecionada)">🖨️ Imprimir</button>
          <button class="btn-fechar" @click="fecharDetalhes">Fechar</button>
        </div>
        <div class="modal-footer" v-else>
          <button class="btn-acao" style="background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; cursor: pointer;" @click="salvarEdicao" :disabled="salvandoEdicao">
            {{ salvandoEdicao ? '⏳ Salvando...' : '💾 Salvar Alterações' }}
          </button>
          <button class="btn-fechar" @click="cancelarEdicao">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';

// Arquivo limpo: As funções de PDF e o import do html2pdf foram removidos.

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const vendas = ref([]);
const clientes = ref([]);
const produtos = ref([]);
const unidades = ref([]);
const carregando = ref(true);
const vendaSelecionada = ref(null);

// Variáveis para o Modo Edição
const editando = ref(false);
const salvandoEdicao = ref(false);
const carrinhoEdicao = ref([]);
const termoBuscaProduto = ref('');
const mostrarDropdownProduto = ref(false);

const mostrarDropdownBusca = ref(false);

const esconderDropdownAtrasado = () => {
  setTimeout(() => { mostrarDropdownBusca.value = false; }, 200);
};

// Lógica para sugerir Clientes ou ID de Vendas no Dropdown
const sugestoesBusca = computed(() => {
  if (!filtros.busca) return [];
  const termo = filtros.busca.toLowerCase();
  
  const clientesFiltrados = clientes.value
    .filter(c => c.nome.toLowerCase().includes(termo))
    .map(c => ({ tipo: 'cliente', id: c.id, nome: c.nome }));

  const vendasFiltradas = vendas.value
    .filter(v => v.id.toString().includes(termo))
    .map(v => ({ tipo: 'venda', id: v.id, cliente_nome: getNomeCliente(v) }));

  return [...clientesFiltrados, ...vendasFiltradas].slice(0, 8); // Mostra até 8 sugestões
});

const selecionarSugestao = (s) => {
  if (s.tipo === 'cliente') {
    filtros.busca = s.nome;
  } else if (s.tipo === 'venda') {
    filtros.busca = s.id.toString();
  }
  mostrarDropdownBusca.value = false;
};

// Propriedade computada que filtra a tabela em tempo real com base nos 3 campos!
const vendasExibidas = computed(() => {
  return vendas.value.filter(v => {
    let passaBusca = true;
    let passaData = true;
    let passaStatus = true;

    if (filtros.busca) {
      const termo = filtros.busca.toLowerCase();
      const nome = getNomeCliente(v).toLowerCase();
      passaBusca = v.id.toString().includes(termo) || nome.includes(termo);
    }

    if (filtros.data && v.data_venda) {
      const dataVendaStr = v.data_venda.split('T')[0]; // Pega apenas a data "YYYY-MM-DD"
      passaData = dataVendaStr === filtros.data;
    }

    if (filtros.status !== 'Todas') {
      const statusVenda = v.status ? v.status.toUpperCase() : 'CONCLUIDA';
      if (filtros.status === 'Concluídas') passaStatus = statusVenda === 'CONCLUIDA';
      if (filtros.status === 'Canceladas') passaStatus = statusVenda === 'CANCELADA';
    }

    return passaBusca && passaData && passaStatus;
  });
});

const dataAtual = new Date();
const hoje = `${dataAtual.getFullYear()}-${String(dataAtual.getMonth() + 1).padStart(2, '0')}-${String(dataAtual.getDate()).padStart(2, '0')}`;

const filtros = reactive({
  busca: '',
  data: hoje,
  status: 'Todas'
});

const buscarHistorico = async () => {
  console.log("Payload enviado para o backend:", { ...filtros });
  await carregarVendas();
};

const carregarVendas = async () => {
  carregando.value = true;
  try {
    const [resVendas, resClientes, resProdutos, resUnidades] = await Promise.all([
      fetch(`${API_URL}/vendas/`),
      fetch(`${API_URL}/clientes/`),
      fetch(`${API_URL}/produtos/`),
      fetch(`${API_URL}/unidades/`)
    ]);
    
    if (resClientes.ok) clientes.value = await resClientes.json();
    if (resVendas.ok) vendas.value = await resVendas.json();
    if (resProdutos.ok) produtos.value = await resProdutos.json();
    if (resUnidades.ok) unidades.value = await resUnidades.json();
  } catch (error) {
    console.error("Erro ao carregar histórico de vendas:", error);
  } finally {
    carregando.value = false;
  }
};

const getNomeCliente = (venda) => {
  // Se a API retornar o objeto aninhado perfeitamente
  if (venda.cliente && venda.cliente.nome) return venda.cliente.nome; 
  // Se a API retornar apenas o cliente_id da nota
  if (venda.cliente_id) {
    const cli = clientes.value.find(c => c.id === venda.cliente_id);
    if (cli) return cli.nome;
  }
  return 'Consumidor Final';
};

const formatarData = (dataStr) => {
  if (!dataStr) return '-';
  const data = new Date(dataStr);
  return data.toLocaleString('pt-BR');
};

const abrirDetalhes = (venda) => {
  vendaSelecionada.value = venda;
};

const fecharDetalhes = () => {
  vendaSelecionada.value = null;
  editando.value = false;
  carrinhoEdicao.value = [];
  termoBuscaProduto.value = '';
};

const esconderDropdownProdutoAtrasado = () => {
  setTimeout(() => { mostrarDropdownProduto.value = false; }, 200);
};

const sugestoesProduto = computed(() => {
  if (!termoBuscaProduto.value) return [];
  const termo = termoBuscaProduto.value.toLowerCase();
  return produtos.value.filter(p => 
    p.nome.toLowerCase().includes(termo) || 
    p.codigo_interno.toLowerCase().includes(termo)
  );
});

const abrirParaEdicao = (venda) => {
  abrirDetalhes(venda);
  iniciarEdicao();
};

const iniciarEdicao = () => {
  editando.value = true;
  carrinhoEdicao.value = vendaSelecionada.value.itens.map(item => {
    const prod = produtos.value.find(p => p.id === item.produto_id);
    return {
      produto_id: item.produto_id,
      produto: prod || { id: item.produto_id, nome: 'Desconhecido', precos: [] },
      unidade_medida_id: item.unidade_medida_id,
      quantidade: parseFloat(item.quantidade),
      preco_unitario_aplicado: parseFloat(item.preco_unitario_aplicado)
    };
  });
};

const cancelarEdicao = () => {
  editando.value = false;
  carrinhoEdicao.value = [];
  termoBuscaProduto.value = '';
};

const adicionarProdutoEdicao = (produto) => {
  const itemExistente = carrinhoEdicao.value.find(i => i.produto_id === produto.id);
  if (itemExistente) {
    itemExistente.quantidade++;
  } else {
    let precoPadrao = 0;
    let unidadeIdPadrao = unidades.value.length > 0 ? unidades.value[0].id : 1;
    if (produto.precos && produto.precos.length > 0) {
      precoPadrao = parseFloat(produto.precos[0].preco_venda);
      unidadeIdPadrao = produto.precos[0].unidade_medida_id || unidadeIdPadrao;
    }
    carrinhoEdicao.value.push({
      produto_id: produto.id,
      produto: produto,
      unidade_medida_id: unidadeIdPadrao,
      quantidade: 1,
      preco_unitario_aplicado: precoPadrao
    });
  }
  termoBuscaProduto.value = '';
  mostrarDropdownProduto.value = false;
};

const atualizarPrecoEdicao = (item) => {
  const precoEncontrado = (item.produto.precos || []).find(p => p.unidade_medida_id === item.unidade_medida_id);
  if (precoEncontrado) {
    item.preco_unitario_aplicado = parseFloat(precoEncontrado.preco_venda);
  }
};

const removerItemEdicao = (index) => {
  carrinhoEdicao.value.splice(index, 1);
};

const totalEdicao = computed(() => {
  return carrinhoEdicao.value.reduce((total, item) => {
    const qtd = parseFloat(item.quantidade) || 0;
    const preco = parseFloat(item.preco_unitario_aplicado) || 0;
    return total + parseFloat((qtd * preco).toFixed(2));
  }, 0);
});

const salvarEdicao = async () => {
  if (carrinhoEdicao.value.length === 0) {
    alert("A nota não pode ficar vazia. Se desejar zerar a nota, feche a edição e utilize o botão de Cancelar Venda.");
    return;
  }
  
  salvandoEdicao.value = true;
  const payload = {
    cliente_id: vendaSelecionada.value.cliente_id,
    valor_total: parseFloat(totalEdicao.value.toFixed(2)),
    itens: carrinhoEdicao.value.map(item => ({
      produto_id: item.produto_id,
      unidade_medida_id: item.unidade_medida_id,
      quantidade: parseFloat(item.quantidade),
      preco_unitario_aplicado: parseFloat(item.preco_unitario_aplicado),
      subtotal: parseFloat((item.quantidade * item.preco_unitario_aplicado).toFixed(2))
    }))
  };

  try {
    const response = await fetch(`${API_URL}/vendas/${vendaSelecionada.value.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      let errorMsg = 'Erro ao atualizar a nota no banco de dados.';
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMsg = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMsg = errorData.detail.map(e => `Campo '${e.loc[e.loc.length - 1]}': ${e.msg}`).join(' | ');
        } else {
          errorMsg = JSON.stringify(errorData.detail);
        }
      }
      throw new Error(errorMsg);
    }
    
    await carregarVendas();
    alert("Venda editada com sucesso!");
    fecharDetalhes();
  } catch (error) {
    alert(error.message);
  } finally {
    salvandoEdicao.value = false;
  }
};

const getNomeProduto = (id) => {
  const prod = produtos.value.find(p => p.id === id);
  return prod ? prod.nome : `Prod #${id}`;
};

const getSiglaUnidade = (id) => {
  const unid = unidades.value.find(u => u.id === id);
  return unid ? unid.sigla : 'UN';
};

const imprimirRecibo = (venda) => {
  const numeroNota = String(venda.id).padStart(9, '0');
  const dataEmissao = formatarData(venda.data_venda).split(' ')[0];
  const horaEmissao = formatarData(venda.data_venda).split(' ')[1] || '-';
  
  let clienteNome = 'Consumidor Final';
  let clienteDoc = '-';
  if (venda.cliente) {
    clienteNome = venda.cliente.nome;
    clienteDoc = venda.cliente.cpf_cnpj || '-';
  } else if (venda.cliente_id) {
    const cli = clientes.value.find(c => c.id === venda.cliente_id);
    if (cli) {
      clienteNome = cli.nome;
      clienteDoc = cli.cpf_cnpj || '-';
    }
  }

  let itensHtml = '';
  if (venda.itens) {
    itensHtml = venda.itens.map(item => {
      const prod = produtos.value.find(p => p.id === item.produto_id);
      const unid = unidades.value.find(u => u.id === item.unidade_medida_id);
      const nomeProd = prod ? prod.nome : `Produto #${item.produto_id}`;
      const codigoProd = prod ? prod.codigo_interno : item.produto_id;
      const siglaUnid = unid ? unid.sigla : 'UN';
      return `
        <tr>
          <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: center;">${codigoProd}</td>
          <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px;">${nomeProd}</td>
          <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: right;">${parseFloat(item.quantidade).toString()}</td>
          <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: center;">${siglaUnid}</td>
          <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: right;">${parseFloat(item.preco_unitario_aplicado).toFixed(2).replace('.', ',')}</td>
          <td style="border-bottom: 1px solid #000; padding: 6px; text-align: right;">${parseFloat(item.subtotal).toFixed(2).replace('.', ',')}</td>
        </tr>
      `;
    }).join('');
  }

  let conteudo = `
    <div style="font-family: Arial, Helvetica, sans-serif; width: 800px; margin: 0 auto; background-color: #fff; color: #000; border: 1px solid #000; padding: 0; box-sizing: border-box; font-size: 11px;">
      
      <!-- CABEÇALHO -->
      <div style="padding: 15px; border-bottom: 1px solid #000;">
        <h2 style="margin: 0; font-size: 24px; font-weight: bold;">Super Feirão das frutas</h2>
        <p style="margin: 5px 0 0 0; font-size: 14px;">Farmaceutica Nenem Borges, Centro, 295</p>
      </div>

      <!-- DESTINATÁRIO/REMETENTE -->
      <div style="font-size: 12px; font-weight: bold; border-bottom: 1px solid #000; padding: 4px 8px; background-color: #f9f9f9;">
        DESTINATÁRIO / REMETENTE
      </div>
      <table style="width: 100%; border-collapse: collapse; border-bottom: 1px solid #000; font-size: 11px;">
        <tr>
          <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px;" colspan="2">NOME / RAZÃO SOCIAL<br><strong style="font-size: 13px;">${clienteNome}</strong></td>
          <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; width: 25%;">CNPJ/CPF<br><strong style="font-size: 13px;">${clienteDoc}</strong></td>
          <td style="padding: 6px; border-bottom: 1px solid #000; width: 20%;">DATA DA EMISSÃO<br><strong style="font-size: 13px;">${dataEmissao}</strong></td>
        </tr>
        <tr>
          <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px;" colspan="2">ENDEREÇO<br><strong style="font-size: 13px;">Endereço não informado</strong></td>
          <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px;">BAIRRO/DISTRITO<br><strong style="font-size: 13px;">-</strong></td>
          <td style="padding: 6px; border-bottom: 1px solid #000;">CEP<br><strong style="font-size: 13px;">-</strong></td>
        </tr>
        <tr>
          <td style="border-right: 1px solid #000; padding: 6px;">MUNICÍPIO<br><strong style="font-size: 13px;">-</strong></td>
          <td style="border-right: 1px solid #000; padding: 6px; width: 10%;">UF<br><strong style="font-size: 13px;">-</strong></td>
          <td style="border-right: 1px solid #000; padding: 6px;">FONE/FAX<br><strong style="font-size: 13px;">-</strong></td>
          <td style="padding: 6px;">HORA DE SAÍDA<br><strong style="font-size: 13px;">${horaEmissao}</strong></td>
        </tr>
      </table>

      <!-- TABELA DE PRODUTOS -->
      <div style="font-size: 12px; font-weight: bold; border-bottom: 1px solid #000; padding: 4px 8px; background-color: #f9f9f9;">
        DADOS DOS PRODUTOS / SERVIÇOS
      </div>
      <table style="width: 100%; border-collapse: collapse; border-bottom: 1px solid #000; font-size: 11px;">
        <thead>
          <tr style="background-color: #f0f0f0;">
            <th style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: center;">CÓDIGO</th>
            <th style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: left;">DESCRIÇÃO DO PRODUTO/SERVIÇO</th>
            <th style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: right;">QTD</th>
            <th style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: center;">UN</th>
            <th style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: right;">VLR. UNIT.</th>
            <th style="border-bottom: 1px solid #000; padding: 6px; text-align: right;">VLR. TOTAL</th>
          </tr>
        </thead>
        <tbody>
          ${itensHtml || `
          <tr>
            <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: center;">1</td>
            <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px;">banana</td>
            <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: right;">14</td>
            <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: center;">CX</td>
            <td style="border-right: 1px solid #000; border-bottom: 1px solid #000; padding: 6px; text-align: right;">55,00</td>
            <td style="border-bottom: 1px solid #000; padding: 6px; text-align: right;">770,00</td>
          </tr>
          `}
        </tbody>
      </table>

      <!-- CÁLCULO DE IMPOSTOS E TOTAIS -->
      <div style="font-size: 12px; font-weight: bold; border-bottom: 1px solid #000; padding: 4px 8px; background-color: #f9f9f9;">
        CÁLCULO DO IMPOSTO / TOTAIS
      </div>
      <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
        <tr>
          <td style="border-right: 1px solid #000; padding: 6px; width: 33.33%;">VALOR DO FRETE<br><strong style="float: right; font-size: 14px;">0,00</strong></td>
          <td style="border-right: 1px solid #000; padding: 6px; width: 33.33%;">DESCONTO<br><strong style="float: right; font-size: 14px;">0,00</strong></td>
          <td style="padding: 6px; width: 33.34%;">VALOR TOTAL DOS PRODUTOS<br><strong style="float: right; font-size: 14px;">${parseFloat(venda.valor_total).toFixed(2).replace('.', ',')}</strong></td>
        </tr>
      </table>

    </div>
  `;

  const janela = window.open('', '', 'width=900,height=800');
  if (janela) {
    janela.document.write('<html><head><title>NFE #' + venda.id + '</title></head><body style="margin:0; padding:20px; display:flex; justify-content:center;">');
    janela.document.write(conteudo);
    janela.document.write('</body></html>');
    janela.document.close();
    janela.focus();
    setTimeout(() => {
      janela.print();
      janela.close();
    }, 250);
  } else {
    alert("Por favor, permita pop-ups no seu navegador para imprimir o recibo.");
  }
};

const apagarVenda = async (id) => {
  if (!confirm(`Tem certeza que deseja cancelar (apagar) a venda #${id}? Esta ação não pode ser desfeita e removerá os registros do faturamento.`)) return;
  
  try {
    const response = await fetch(`${API_URL}/vendas/${id}`, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      carregarVendas();
    } else {
      const data = await response.json();
      alert(data.detail || 'Erro ao cancelar a venda.');
    }
  } catch (error) {
    alert('Erro de conexão ao tentar cancelar a venda.');
  }
};

onMounted(() => {
  carregarVendas();
});
</script>

<style scoped>
.container { max-width: 1200px; margin: 0 auto; padding: 20px; font-family: sans-serif; box-sizing: border-box; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header h2 { margin: 0; color: #334155; }

/* Estilos da Barra de Filtros */
.filtros-bar {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 20px;
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  flex-wrap: wrap;
}
.filtro-grupo { display: flex; }
.flex-grow { flex-grow: 1; min-width: 200px; }
.btn-direita { margin-left: auto; }
.input-filtro {
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 1rem;
  background-color: #fff;
  color: #374151;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-filtro:focus {
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2);
}
.btn-buscar { padding: 10px 20px; background-color: #16a34a; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 1rem; transition: background-color 0.2s; white-space: nowrap; }
.btn-buscar:hover { background-color: #15803d; }

/* Estilos do Dropdown de Busca */
.search-wrapper { position: relative; }
.dropdown-sugestoes { position: absolute; top: 100%; left: 0; right: 0; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(8px); border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px; list-style: none; margin: 0; padding: 0; max-height: 250px; overflow-y: auto; z-index: 1000; box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
.dropdown-sugestoes li { padding: 12px 15px; cursor: pointer; border-bottom: 1px solid #eee; color: #333; font-size: 1.05rem; }
.dropdown-sugestoes li:hover { background: rgba(46, 125, 50, 0.1); color: #2e7d32; }

.card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.loading { text-align: center; color: #666; font-size: 1.1rem; padding: 40px; }
.table { width: 100%; border-collapse: collapse; border: 1px solid #ddd; }
.table th { padding: 12px 10px; border: 1px solid #ddd; border-bottom: 2px solid #ccc; color: #333; background-color: #f8f9fa; }
.table td { padding: 15px 10px; border: 1px solid #ddd; color: #444; }
.table tbody tr:nth-child(even) { background-color: #f9f9f9; }
.table tbody tr:hover { background-color: #f1f8e9; transition: background-color 0.2s; }
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }
.col-id { width: 80px; }
.col-acoes { width: 310px; }
.btn-acao { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: background-color 0.2s; display: inline-flex; align-items: center; justify-content: center; }
.btn-acao.del { background-color: #f44336; color: white; }
.btn-acao.del:hover { background-color: #d32f2f; }
.btn-acao.print { background-color: #2196F3; color: white; margin-right: 8px; }
.btn-acao.print:hover { background-color: #1976D2; }
.btn-acao.edit { background-color: #ff9800; color: white; margin-right: 8px; }
.btn-acao.edit:hover { background-color: #f57c00; }
.empty-state { text-align: center; color: #888; font-style: italic; padding: 30px !important; }
.codigo { font-family: monospace; color: #888; }
.valor-total { font-weight: bold; color: #2e7d32; }

.linha-clicavel { cursor: pointer; }
.linha-clicavel:hover { background-color: #e8f5e9 !important; }

/* Modal Styles */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: #fff; border-radius: 8px; width: 90%; max-width: 600px; max-height: 90vh; display: flex; flex-direction: column; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; border-bottom: 1px solid #ddd; background: #f8f9fa; border-radius: 8px 8px 0 0; }
.modal-header h3 { margin: 0; color: #2e7d32; }
.btn-fechar-icon { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #888; }
.btn-fechar-icon:hover { color: #333; }
.modal-body { padding: 20px; overflow-y: auto; }
.info-resumo { display: flex; justify-content: space-between; flex-wrap: wrap; margin-bottom: 20px; background: #f1f8e9; padding: 15px; border-radius: 6px; border: 1px solid #c8e6c9; }
.info-resumo p { margin: 5px 0; width: 48%; }
.table-itens { width: 100%; border-collapse: collapse; margin-top: 10px; }
.table-itens th, .table-itens td { padding: 10px; border-bottom: 1px solid #eee; text-align: left; }
.table-itens th { background: #fafafa; color: #555; }
.modal-footer { padding: 15px 20px; border-top: 1px solid #ddd; display: flex; justify-content: flex-end; gap: 10px; background: #f8f9fa; border-radius: 0 0 8px 8px; }
.btn-fechar { padding: 8px 16px; background-color: #e0e0e0; color: #333; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
.btn-fechar:hover { background-color: #ccc; }

/* Estilos para o Modo de Edição */
.edit-table td { vertical-align: middle; }
.input-mini { width: 70px; padding: 6px; border: 1px solid #c8e6c9; background: #f1f8e9; border-radius: 6px; outline: none; text-align: right; font-size: 0.95rem; color: #2e7d32; font-weight: 500; }
.input-mini:focus { border-color: #4CAF50; background: #fff; box-shadow: 0 0 5px rgba(76,175,80,0.2); color: #333; }
.input-mini-select { width: 75px; padding: 6px; border: 1px solid #c8e6c9; background: #f1f8e9; border-radius: 6px; outline: none; color: #2e7d32; text-align: center; font-weight: 500; }
.input-mini-select:focus { border-color: #4CAF50; background: #fff; }
.input-preco { width: 85px; padding: 6px; border: 1px solid #c8e6c9; background: #f1f8e9; border-radius: 6px; outline: none; text-align: right; font-size: 0.95rem; color: #2e7d32; font-weight: 500; }
.input-preco:focus { border-color: #4CAF50; background: #fff; }
.btn-remover { background: transparent; border: none; padding: 5px; font-size: 1.3rem; cursor: pointer; transition: transform 0.2s; }
.btn-remover:hover { transform: scale(1.2); }
.busca-edicao-wrapper { position: relative; margin-top: 20px; }
.input-busca-edicao { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1.05rem; outline: none; transition: border-color 0.3s; }
.input-busca-edicao:focus { border-color: #2e7d32; box-shadow: 0 0 8px rgba(46,125,50,0.2); }
</style>