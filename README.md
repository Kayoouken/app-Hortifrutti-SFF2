# SFF2 (Super Feirão das Frutas 2) 🍎🥦

Sistema Full-Stack de Frente de Caixa (PDV) e Gestão (ERP) focado no varejo de hortifruti. Desenvolvido do zero para criar um fluxo de vendas ágil para os caixas e um painel de gestão eficiente, garantindo a integridade dos dados e uma ótima experiência de uso (UX).

## 💻 Tecnologias Utilizadas

*   **Frontend:** Vue.js 3 (Composition API), HTML5, CSS3 avançado (Flexbox, Grid).
*   **Backend:** Python 3, FastAPI.
*   **Banco de Dados & ORM:** SQLite / SQLAlchemy.
*   **Validação de Dados:** Pydantic.

## 🚀 Principais Funcionalidades e Desafios Resolvidos

### 1. Controle de Transações ACID (Integridade Financeira)
A rota de finalização de vendas (`/vendas/`) utiliza `db.commit()` e `db.rollback()` atômicos no SQLAlchemy. Isso garante que uma venda só seja registrada no banco de dados se **todos** os seus itens também forem salvos corretamente. Se ocorrer qualquer falha na validação de valores totais ou erro de rede, o sistema reverte a operação, prevenindo itens de venda "órfãos".

### 2. Modelagem Relacional Complexa
Um produto pode ter múltiplos preços baseados na Unidade de Medida (KG, CX, UN). A arquitetura do banco foi construída com tabelas de junção (`ProdutoPreco`) e `UniqueConstraint` para impedir que o sistema ou o usuário dupliquem regras de negócio, delegando a consistência dos dados ao banco.

### 3. Validação Estrita de Dados
Uso intensivo do **Pydantic** no FastAPI. O backend exige tipagem estrita (como `Decimal` para dados financeiros, prevenindo erros de arredondamento) antes da requisição atingir a lógica de negócio ou o banco de dados.

### 4. Reatividade e UX Avançada
*   **Busca em Tempo Real (Debounce):** Inputs de busca de clientes e produtos utilizam propriedades computadas do Vue 3 para filtrar dados em memória conforme o usuário digita, sem necessidade de recarregar a tela.
*   **Edição Expressa:** Interfaces em formato de planilha que salvam dados de forma assíncrona, oferecendo um uso rápido e sem interrupções.
*   **Imutabilidade de Histórico:** Alterações de preços atuais não afetam os recibos e histórico de vendas já finalizadas, garantindo segurança fiscal/gerencial.

## ⚙️ Como executar o projeto localmente

**1. Clone o repositório:**
```bash
git clone https://github.com/SEU_USUARIO/app_SFF2.git
```

*(Adicione aqui as instruções para rodar o backend com `uvicorn main:app --reload` e o frontend com `npm run dev`)*