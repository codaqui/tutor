# Codaqui Intranet

## Objetivo

A ideia básica é criar um sistema que o aluno consiga criar sua conta com o GitHub e acessar a intranet da Codaqui.

- [X] Sistema de login via GitHub.
  - [X] Receber convite para fazer parte do time: https://github.com/orgs/codaqui/teams/intranet
  - [X] Validar se a pessoa faz parte do time no GitHub.
- [X] Perfil de Estudante
- [X] Criar um sistema de completar o cadastro.
- [X] Sistema de Carteira
  - [X] Usuário poder ter uma carteira.
    - [X] A ativação da conta é feita por uma custom action e automaticamente cria a carteira.
  - [X] Usuário pode consultar seus pontos.
  - [X] Usuário pode consultar histórico de transações na sua conta.
- [ ] Criar um repositório para salvar as Issues da Intranet.
  - [ ] Criar um repositório para salvar as Issues da Intranet.
  - [ ] Criar um repositório para salvar as Issues da Intranet.
- [X] GitHub Service
  - [X] Consumir rotas da API com o App GitHub.
- [ ] Sistema de Tarefas (Integração com o GitHub)
  - [ ] Usuário o pode ver as tarefas disponíveis.
  - [ ] O usuário pode se candidatar a uma tarefa disponível.
  - [ ] O usuário pode solicitar ajuda/mais informações sobre a tarefa que está realizando.
  - [ ] O usuário pode concluir (enviar para analise) a tarefa.
  - [ ] O usuário pode saber o resultado da analise.
- [ ] Atualizar a Wallet para poder associar uma Issue na transação. (opcional)
- [ ] Loja Virtual
  - [ ] Escolher item.
  - [ ] Revisão.
- [ ] Testes Básicos
- [ ] Pré - Deploy - v1
  - [ ] Lint e iSort do Projeto
  - [ ] Escolher um Postgres da vida.
  - [ ] Utilizar o Replit agora é factivel ou vamos para Azure.
- [ ] Rever fluxos de formulários, verificar se tem como cair em alguma exceção.
- [ ] Criar página para editar perfil separada, para facilitar manutenção.
- [ ] Resetar o banco de dados e partir como v1.

### Futuros Apps

- [ ] App de Integração com o Discord
  - [ ] Presença em Monitoria/Encontro
  - [ ] Mensagem automática de Encontro e Resumo do Encontro
  - [ ] Pontos automáticos para lista de presença.
- [ ] Bot de Discord
  - [ ] Ranking de Pontuação
  - [ ] Consultar/Editar perfil
  - [ ] Vinculo de Perfil do Discord para Perfil da Codaqui
    - [ ] Modelo do Discord
    - [ ] 1:1 com Stundent
    - [ ] Integração de Carteira e Pontos

### Melhorias de Infraestrutura

- [ ] Cobertura de Testes
- [ ] Modo de Desenvolvimento com Docker

## Desenvolvimento


### Criando dotenv 

```dosini
GITHUB_OAUTH_SECRET=""
GITHUB_OAUTH_CLIENT_ID=""
SECRET_KEY=""
GH_APP_INSTALL_ID=""
GH_APP_ID=""
```

### Executando o Projeto

```bash
poetry install
poetry run python manage.py migrate 
poetry run python manage.py runserver
```

### Criando um Super Usuário

```bash
poetry run python manage.py createsuperuser
```

### Criando um App

```bash
poetry run python manage.py startapp <nome_do_app>
```

### Criando um Modelo

```bash
poetry run python manage.py makemigrations
```

## Tecnologia

- [Python](https://www.python.org/)
- [Poetry](https://python-poetry.org/)
- [Django](https://www.djangoproject.com/)
