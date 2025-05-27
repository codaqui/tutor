#!/bin/bash
set -e

# Expected output from Ollama server
EXPECTED_OUTPUT="Ollama is running"
MAX_RETRIES=10  # Número de tentativas
SLEEP_TIME=5    # Segundos entre tentativas

# Iniciar o servidor Ollama em segundo plano para a criação do modelo
echo "⏳ Iniciando servidor Ollama temporário para criação do modelo..."
OLLAMA_HOST=127.0.0.1:11155 /usr/bin/ollama serve &
serve_pid=$!

echo "⏳ Aguardando o servidor Ollama temporário (PID: $serve_pid) ficar pronto..."

# Aguardar o Ollama estar pronto
i=1
while [ $i -le $MAX_RETRIES ]; do
    echo "🔄 Tentativa $i/$MAX_RETRIES para verificar se o servidor Ollama está rodando..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:11155 || echo "000")
    RESPONSE_BODY=""

    if [ "$HTTP_CODE" = "200" ]; then
        RESPONSE_BODY=$(curl -s http://localhost:11155 || echo "")
    fi

    if [ "$RESPONSE_BODY" = "$EXPECTED_OUTPUT" ]; then
        echo "✅ Servidor Ollama temporário está rodando (Tentativa $i)"
        break
    fi

    echo "⏳ Tentativa $i/$MAX_RETRIES falhou (HTTP Code: $HTTP_CODE). Tentando novamente em $SLEEP_TIME segundos..."
    sleep $SLEEP_TIME
    i=$((i+1))
done

# Se o loop completar sem quebrar, o Ollama não iniciou com sucesso
if [ "$RESPONSE_BODY" != "$EXPECTED_OUTPUT" ]; then # Alterado de [[ para [
    echo "❌ Servidor Ollama temporário não iniciou em $((MAX_RETRIES * SLEEP_TIME)) segundos"
    echo "Output do servidor Ollama (PID: $serve_pid):"
    kill $serve_pid
    wait $serve_pid 2>/dev/null || true
    exit 1
fi

# Variável para o nome do modelo, para facilitar a alteração
MODEL_NAME="codaqui"

# Continuar com a criação do modelo
echo "🔄 Criando modelo: $MODEL_NAME a partir de /app/Modelfile..."
if OLLAMA_HOST=127.0.0.1:11155 /usr/bin/ollama create "$MODEL_NAME" -f /app/Modelfile; then
    echo "✅ Modelo $MODEL_NAME criado com sucesso"
else
    echo "❌ Falha ao criar o modelo $MODEL_NAME!"
    kill $serve_pid
    wait $serve_pid 2>/dev/null || true
    exit 1
fi

# Desligar o servidor Ollama temporário
echo "🔄 Parando servidor Ollama temporário (PID: $serve_pid)..."
kill $serve_pid
wait $serve_pid 2>/dev/null || true  # Garantir desligamento gracioso
echo "✅ Servidor Ollama temporário desligado com sucesso"

# Iniciar o Ollama em primeiro plano na porta correta (para que o contêiner continue rodando)
echo "🚀 Iniciando servidor Ollama principal em 0.0.0.0:11434..."
export OLLAMA_HOST=0.0.0.0:11434
exec /usr/bin/ollama serve