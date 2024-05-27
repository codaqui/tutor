# Codaqui Intranet

## Objetivo

A ideia básica é criar um sistema que o aluno consiga criar sua conta com o GitHub e acessar a intranet da Codaqui.

- [X] Sistema de login via GitHub.
- [X] Perfil de Estudante
- [ ] Criar um sistema de completar o cadastro.
- [ ] Desenhar a ideia de Develop Bounty
  - Sistema de Cadastro de Tasks
    - Pontuação
  - Pode pegar a task e dizer quando vai entregar ou se comprometer com a data solicitada.
  - Ganhar pontos por tasks.
  - CodaPoints ----> Dinheiro (conforme a conta bancária)
    - Pode trocar por cursos, livros, etc.
    - Codapoints (total de pontos existem para ser trocados // saldo da conta)
    - 1 real - 1 ponto

## Desenvolvimento

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