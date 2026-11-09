README - Sistema de Gestão de Oficinas
📌 Sobre o Projeto

O Sistema de Gestão de Oficinas é um MVP (Produto Mínimo Viável) desenvolvido para a Associação de Moradores do Bairro Santa Helena, com o objetivo de substituir o controle manual realizado em fichas de papel e planilhas.

A solução busca facilitar o cadastro de participantes, o controle de frequência e a geração de relatórios, tornando a gestão das oficinas mais organizada e eficiente.

🎯 Problema

Atualmente, a associação realiza o controle de inscrições e frequência de forma manual, o que gera:

Perda de informações;
Retrabalho administrativo;
Dificuldade de acompanhar participantes;
Dificuldade na prestação de contas e geração de relatórios.
👥 Público-Alvo
Usuários Diretos
Presidente da associação;
Voluntários responsáveis pela administração das oficinas.
Beneficiados Indiretamente
Moradores participantes das oficinas;
Crianças, adolescentes, adultos e idosos da comunidade;
Parceiros e apoiadores da associação.
🚀 Objetivo do MVP

Desenvolver uma aplicação simples e acessível que permita:

Cadastrar participantes;
Cadastrar oficinas;
Registrar frequência;
Consultar relatórios de participação.
🛠 Tecnologias Utilizadas
Python 3.12
Flask 3.x
HTML5
CSS3
Jinja2
SQLite (biblioteca `sqlite3` do Python)
🏗 Arquitetura

O sistema utiliza o padrão MVC (Model-View-Controller).

Model

Responsável pelo armazenamento e manipulação dos dados.

View

Responsável pela interface e interação com o usuário.

Controller

Responsável pelas regras de negócio e comunicação entre interface e banco de dados.

🚀 Instalação e Execução

### Requisitos

- Python 3.12 ou superior instalado;
- Git;
- PowerShell (Windows).

No PowerShell, acesse a pasta do projeto e crie um ambiente virtual Python:

```powershell
py -3.12 -m venv .venv
```

Ative o ambiente e instale as dependências:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Inicie o servidor local:

```powershell
python main.py
```

Abra `http://127.0.0.1:5000` no navegador. Para encerrar o servidor, pressione `Ctrl+C` no terminal.

### Banco de dados

O SQLite é inicializado automaticamente quando a aplicação inicia. O arquivo
`instance/participantes.sqlite3` é criado localmente e não precisa ser versionado.
Se necessário, com o ambiente virtual ativado, inicialize o banco manualmente:

```powershell
flask --app main init-db
```

### Testes

Com as dependências instaladas, execute a suíte automatizada:

```powershell
python -m unittest discover -s tests -v
```

O cadastro e a consulta de participantes, oficinas e frequências, além dos relatórios com filtros,
estão disponíveis nos links da página inicial.

É possível definir a chave de sessão em produção pela variável de ambiente `SECRET_KEY`.

Estrutura inicial:

```text
app/
  templates/
  __init__.py
  routes.py
main.py
requirements.txt
```

🗄 Banco de Dados
SQLite

Entidades principais:

Participante
id_participante
nome
telefone
data_nascimento
endereço
status
Oficina
id_oficina
nome_oficina
descrição
data_inicio
data_fim
status
Frequência
id_frequencia
id_participante
id_oficina
data_presenca
presente
✅ Requisitos Funcionais
RF01

Cadastrar participantes.

RF02

Cadastrar oficinas.

RF03

Registrar frequência dos participantes.

RF04

Gerar relatórios de participação.

RF05 (Desejável)

Pesquisar participantes por nome.

🔒 Segurança

O sistema implementa:

Autenticação de usuários;
Senhas protegidas com PBKDF2;
Controle de acesso às funcionalidades;
Proteção contra SQL Injection através do SQLAlchemy;
Proteção contra XSS utilizando Jinja2;
Validação de dados no cliente e no servidor.
♿ Acessibilidade

O projeto foi desenvolvido considerando:

Interface responsiva para dispositivos móveis;
Áreas de toque com pelo menos 44 px;
Rótulos visíveis nos formulários;
Alto contraste entre texto e fundo;
Navegação por teclado com indicador de foco e link para pular ao conteúdo;
Tabelas com rolagem horizontal acessível em telas estreitas;
Mensagens de erro claras;
Navegação simples para usuários com pouca experiência tecnológica.
🌎 ODS Relacionado
ODS 4 - Educação de Qualidade

O sistema contribui para melhorar a gestão das oficinas educacionais da associação, permitindo um acompanhamento mais eficiente dos participantes e fortalecendo as ações de aprendizagem da comunidade.

📱 Telas Principais
1. Menu Inicial
Acesso às funcionalidades principais;
Navegação simples e intuitiva.
2. Registro de Frequência
Seleção de participante e oficina;
Registro de presença.
3. Relatórios
Consulta de frequências;
Pesquisa e acompanhamento das atividades.
📈 Resultados Esperados
Redução do uso de papel;
Diminuição do retrabalho administrativo;
Melhor organização das oficinas;
Maior controle da participação dos alunos;
Facilidade na emissão de relatórios.
👨‍💻 Autor

Projeto desenvolvido como atividade acadêmica do curso de Análise e Desenvolvimento de Sistemas, voltado à aplicação de conceitos de requisitos, arquitetura de software, modelagem de dados, acessibilidade e desenvolvimento centrado no usuário.