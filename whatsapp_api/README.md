# WhatsApp API com Baileys e PostgreSQL

Esta API permite integrar o WhatsApp em suas aplicações usando o Baileys com autenticação persistente via PostgreSQL.

## Recursos

- Autenticação persistente usando PostgreSQL
- Envio de mensagens de texto, imagem, áudio e vídeo
- API REST para integração fácil
- Suporte para mensagens de grupo
- Internacionalização/localização (i18n)

## Requisitos

- Node.js 16+
- PostgreSQL 12+
- Dependências do projeto

## Instalação

1. Clone o repositório
2. Instale as dependências:

```bash
npm install
```

3. Configure o arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

4. Ajuste as variáveis de ambiente no arquivo `.env` conforme sua configuração.

## Uso com Docker

A maneira mais fácil de executar o projeto é usando Docker:

```bash
docker-compose up -d
```

Isso iniciará o serviço WhatsApp API e o PostgreSQL.

## Uso sem Docker

1. Certifique-se de ter um banco de dados PostgreSQL acessível.
2. Configure o arquivo `.env` com os dados de conexão.
3. Execute o servidor:

```bash
npm start
```

4. Escaneie o código QR que aparecerá no console usando o WhatsApp do seu celular.

## Endpoints da API

### Enviar mensagem de texto

```
POST /send/text
```

Corpo da requisição:
```json
{
  "jid": "55219XXXXXXXX@s.whatsapp.net",
  "message": "Olá, esta é uma mensagem de teste!"
}
```

### Enviar imagem

```
POST /send/image
```

Corpo da requisição:
```json
{
  "jid": "55219XXXXXXXX@s.whatsapp.net",
  "url": "https://exemplo.com/imagem.jpg",
  "caption": "Legenda opcional"
}
```

### Enviar vídeo

```
POST /send/video
```

Corpo da requisição:
```json
{
  "jid": "55219XXXXXXXX@s.whatsapp.net",
  "url": "https://exemplo.com/video.mp4",
  "caption": "Legenda opcional"
}
```

### Enviar áudio

```
POST /send/audio
```

Corpo da requisição:
```json
{
  "jid": "55219XXXXXXXX@s.whatsapp.net",
  "url": "https://exemplo.com/audio.mp3",
  "ptt": true
}
```

## Nota sobre JIDs

Os JIDs (Jabber IDs) para WhatsApp seguem o seguinte formato:
- Usuários: `[número com código do país]@s.whatsapp.net`
- Grupos: `[id-do-grupo]@g.us`

## Licença

Este projeto está licenciado sob a licença MIT.
