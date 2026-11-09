# Documentação do MVP

## Contexto e objetivo

O Sistema de Gestão de Oficinas apoia a Associação de Moradores do Bairro Santa
Helena na organização de participantes, oficinas e frequências, substituindo
controles manuais em papel e planilhas. O MVP é uma aplicação web local, em
português, com persistência em SQLite.

## Requisitos

### Requisitos funcionais

| ID | Requisito | Situação |
| --- | --- | --- |
| RF01 | Cadastrar e consultar participantes. | Implementado |
| RF02 | Cadastrar e consultar oficinas. | Implementado |
| RF03 | Registrar presença ou ausência de um participante em uma oficina por data. | Implementado |
| RF04 | Consultar relatórios de frequência, com filtros por participante e oficina e resumo de presenças e ausências. | Implementado |
| RF05 | Pesquisar participantes por nome. | Desejável; ainda não implementado como filtro |

O cadastro de participante exige nome. O cadastro de oficina exige nome,
descrição e data de início. O registro de frequência exige participante,
oficina, data e situação (presente ou ausente). O sistema valida os campos e
impede mais de um registro para o mesmo participante, oficina e data.

### Requisitos não funcionais

- **RNF01 — Usabilidade:** interface em português, com rótulos visíveis,
  mensagens para o usuário e navegação simples.
- **RNF02 — Responsividade e acessibilidade:** layout adaptável a telas
  estreitas, navegação por teclado, indicador de foco, link para pular ao
  conteúdo, áreas de interação de pelo menos 44 px e rolagem horizontal
  acessível para tabelas largas.
- **RNF03 — Integridade:** chaves estrangeiras relacionam frequências a
  participantes e oficinas; campos obrigatórios e estados válidos são
  verificados pela aplicação e pelo SQLite.
- **RNF04 — Persistência local:** dados mantidos em
  `instance/participantes.sqlite3`, criado automaticamente na inicialização.
- **RNF05 — Segurança de consultas:** comandos SQL usam parâmetros para os
  dados fornecidos pelo usuário; os templates Jinja escapam valores por padrão.

## Arquitetura

A aplicação segue uma organização MVC simplificada, sem uma camada de modelos
ORM:

| Camada | Responsabilidade | Implementação |
| --- | --- | --- |
| Inicialização | Configurar a aplicação Flask, a chave de sessão e o caminho do banco; registrar rotas e inicializar o esquema. | `main.py`, `app/__init__.py` |
| Controle | Receber requisições HTTP, validar dados, aplicar regras e consultar ou alterar o banco. | `app/routes.py` |
| Dados | Abrir e encerrar a conexão SQLite por contexto e criar tabelas. | `app/database.py` |
| Apresentação | Renderizar as páginas HTML com Jinja e estilos adaptáveis. | `app/templates/`, `app/static/styles.css` |

### Principais rotas

| Método | Rota | Função |
| --- | --- | --- |
| GET | `/` | Exibe o menu inicial. |
| GET, POST | `/participantes` | Lista e cadastra participantes. |
| GET, POST | `/oficinas` | Lista e cadastra oficinas. |
| GET, POST | `/frequencias` | Consulta e registra frequências. |
| GET | `/relatorios` | Consulta frequências, opcionalmente filtradas por participante e oficina. |

## Modelo de dados

O banco contém três entidades. Datas são armazenadas como texto no formato
ISO `AAAA-MM-DD`.

### `participantes`

| Campo | Tipo SQLite | Regra |
| --- | --- | --- |
| `id_participante` | INTEGER | Chave primária autoincrementada. |
| `nome` | TEXT | Obrigatório; até 200 caracteres na aplicação. |
| `telefone` | TEXT | Opcional; até 30 caracteres na aplicação. |
| `data_nascimento` | TEXT | Opcional; validada como data quando informada. |
| `endereco` | TEXT | Opcional; até 300 caracteres na aplicação. |
| `status` | TEXT | Obrigatório; `ativo` ou `inativo`; padrão `ativo`. |

### `oficinas`

| Campo | Tipo SQLite | Regra |
| --- | --- | --- |
| `id_oficina` | INTEGER | Chave primária autoincrementada. |
| `nome_oficina` | TEXT | Obrigatório; até 200 caracteres na aplicação. |
| `descricao` | TEXT | Obrigatório; até 2000 caracteres na aplicação. |
| `data_inicio` | TEXT | Obrigatório; data válida. |
| `data_fim` | TEXT | Opcional; quando informada, não pode anteceder o início. |
| `status` | TEXT | Obrigatório; `ativa` ou `inativa`; padrão `ativa`. |

### `frequencias`

| Campo | Tipo SQLite | Regra |
| --- | --- | --- |
| `id_frequencia` | INTEGER | Chave primária autoincrementada. |
| `id_participante` | INTEGER | Obrigatório; chave estrangeira para `participantes.id_participante`. |
| `id_oficina` | INTEGER | Obrigatório; chave estrangeira para `oficinas.id_oficina`. |
| `data_presenca` | TEXT | Obrigatório; data válida. |
| `presente` | INTEGER | Obrigatório; somente `0` (ausente) ou `1` (presente). |

O par participante/oficina pode ter no máximo um registro por data. Essa
unicidade é garantida pela restrição `UNIQUE
(id_participante, id_oficina, data_presenca)`.

### Relacionamentos

```text
participantes 1 ─── N frequencias N ─── 1 oficinas
```

Uma frequência pertence a exatamente um participante e a exatamente uma
oficina. Participantes e oficinas podem existir sem registros de frequência.

## Limites conhecidos

- O sistema não possui autenticação ou controle de acesso por usuário.
- O cadastro e a consulta estão disponíveis; edição e exclusão de registros
  não fazem parte deste MVP.
- A pesquisa por nome indicada em RF05 ainda não está implementada.

## Execução e testes

As instruções de instalação, execução local e testes automatizados estão no
[README](../README.md). A suíte pode ser executada com
`python -m unittest discover -s tests -v`.
