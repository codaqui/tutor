# Codaqui Intranet

## Objetivo

A ideia básica é criar um sistema que o aluno consiga criar sua conta com o GitHub e acessar a intranet da Codaqui.

- [X] Sistema de login via GitHub.
- [X] Perfil de Estudante
- [X] Criar um sistema de completar o cadastro.
- [X] Sistema de Carteira
  - [X] Usuário poder ter uma carteira.
    - [ ] Faz sentido a carteira ser criada com o perfil?
    - [X] Faz sentido a carteira ser criada com a ativação?
  - [X] Usuário pode consultar seus pontos.
  - [X] Usuário pode consultar histórico de transações.
- [ ] Sistema de Tarefas
  - [ ] Usuário o pode ver as tarefas disponíveis.
- [ ] Lint e iSort do Projeto
- [ ] Sistema para gerenciar mais fácil alunos que precisam de ativação.
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
