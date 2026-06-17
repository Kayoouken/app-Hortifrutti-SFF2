<template>
  <div class="container">
    <header class="header">
      <h2>Gerenciar Clientes</h2>
    </header>
    
    <!-- Formulário de Cadastro -->
    <div class="form-card">
      <h3 style="margin-top: 0; margin-bottom: 20px;">Cadastrar Novo Cliente</h3>
      <div class="form-row">
        <div class="form-group flex-2">
          <label>Nome Completo *</label>
          <input type="text" v-model="novoCliente.nome" placeholder="Ex: Maria das Graças" />
        </div>
        <div class="form-group">
          <label>CPF / CNPJ</label>
          <input type="text" v-model="novoCliente.cpf_cnpj" placeholder="Apenas números" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Telefone</label>
          <input type="text" v-model="novoCliente.telefone" placeholder="(00) 00000-0000" />
        </div>
        <div class="form-group">
          <label>E-mail</label>
          <input type="email" v-model="novoCliente.email" placeholder="cliente@email.com" />
        </div>
      </div>

      <div v-if="mensagem.texto" :class="['mensagem-alerta', mensagem.tipo]">
        {{ mensagem.texto }}
      </div>

      <div class="form-actions">
        <button class="btn-salvar" @click="salvarCliente" :disabled="salvando">
          {{ salvando ? 'Salvando...' : 'Salvar Cliente' }}
        </button>
      </div>
    </div>

    <!-- Tabela de Clientes Existentes -->
    <div class="clientes-lista">
      <h3>Lista de Clientes Cadastrados</h3>
      <table class="tabela-clientes">
        <thead>
          <tr>
            <th class="text-center col-id">ID</th>
            <th class="text-left">Nome</th>
            <th class="text-center">CPF/CNPJ</th>
            <th class="text-center">Telefone</th>
            <th class="text-center">Cadastrado em</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in clientes" :key="c.id">
            <td class="codigo text-center">#{{ c.id }}</td>
            <td class="text-left"><strong>{{ c.nome }}</strong></td>
            <td class="text-center">{{ c.cpf_cnpj || '-' }}</td>
            <td class="text-center">{{ c.telefone || '-' }}</td>
            <td class="text-center">{{ new Date(c.criado_em).toLocaleDateString('pt-BR') }}</td>
          </tr>
          <tr v-if="clientes.length === 0">
            <td colspan="5" style="text-align: center; padding: 20px; color: #888;">Nenhum cliente cadastrado ainda.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const clientes = ref([]);
const salvando = ref(false);
const mensagem = ref({ texto: '', tipo: '' });

const novoCliente = ref({ nome: '', cpf_cnpj: '', telefone: '', email: '' });

const carregarClientes = async () => {
  try {
    const res = await fetch('http://localhost:8000/clientes/');
    if (res.ok) clientes.value = await res.json();
  } catch (error) {
    console.error("Erro ao carregar clientes", error);
  }
};

onMounted(carregarClientes);

const salvarCliente = async () => {
  if (!novoCliente.value.nome) {
    mensagem.value = { texto: 'O Nome é obrigatório!', tipo: 'erro' };
    return;
  }
  salvando.value = true;
  mensagem.value = { texto: '', tipo: '' };

  // Transforma textos vazios em nulo. O banco de dados permite múltiplos "nulos", 
  // mas acusa duplicidade se tentar salvar várias strings vazias ("") no CPF/CNPJ.
  const payload = {
    nome: novoCliente.value.nome,
    cpf_cnpj: novoCliente.value.cpf_cnpj || null,
    telefone: novoCliente.value.telefone || null,
    email: novoCliente.value.email || null
  };

  try {
    const res = await fetch('http://localhost:8000/clientes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    if (!res.ok) throw new Error('Documento já cadastrado ou erro na API.');
    
    mensagem.value = { texto: '✔ Cliente cadastrado com sucesso!', tipo: 'sucesso' };
    novoCliente.value = { nome: '', cpf_cnpj: '', telefone: '', email: '' }; // Limpa o form
    carregarClientes(); // Atualiza a tabela
  } catch (error) {
    mensagem.value = { texto: error.message, tipo: 'erro' };
  } finally {
    salvando.value = false;
  }
};
</script>

<style scoped>
.container { max-width: 1200px; margin: 0 auto; padding: 20px; font-family: sans-serif; box-sizing: border-box; }
.header { margin-bottom: 20px; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; }
.header h2 { margin: 0; color: #334155; }
.form-card { background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }
.form-row { display: flex; gap: 15px; margin-bottom: 15px; }
.form-group { display: flex; flex-direction: column; flex: 1; }
.flex-2 { flex: 2; }
.form-group label { margin-bottom: 5px; font-weight: bold; color: #555; font-size: 0.9rem; }
.form-group input { padding: 12px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; outline: none; background-color: #fff; color: #333; }
.form-group input:focus { border-color: #2e7d32; box-shadow: 0 0 5px rgba(46,125,50,0.2); }
.form-actions { display: flex; justify-content: flex-end; margin-top: 10px; }
.btn-salvar { padding: 12px 20px; background-color: #2e7d32; color: white; border: none; border-radius: 4px; font-size: 1rem; font-weight: bold; cursor: pointer; }
.btn-salvar:hover:not(:disabled) { background-color: #1b5e20; }
.btn-salvar:disabled { background-color: #a5d6a7; cursor: not-allowed; }
.mensagem-alerta { padding: 10px; margin-bottom: 15px; border-radius: 4px; font-weight: bold; text-align: center; }
.sucesso { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
.erro { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }

.clientes-lista h3 { color: #333; margin-bottom: 15px; }
.tabela-clientes { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.1); border: 1px solid #ddd; }
.tabela-clientes th { background: #f8f9fa; border-bottom: 2px solid #ccc; border-right: 1px solid #ddd; padding: 15px 12px; text-align: left; color: #333; }
.tabela-clientes th:last-child { border-right: none; }
.tabela-clientes td { padding: 15px 12px; border-bottom: 1px solid #eee; border-right: 1px solid #eee; color: #444; }
.tabela-clientes td:last-child { border-right: none; }
.tabela-clientes tbody tr:nth-child(even) { background-color: #f9f9f9; }
.tabela-clientes tbody tr:hover { background-color: #f1f8e9; transition: background-color 0.2s; }
.codigo { font-family: monospace; color: #888; }
.text-left { text-align: left !important; }
.text-center { text-align: center !important; }
.col-id { width: 80px; }
</style>