#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
MODEL_DIR="vosk-model-small-pt-0.3"
MODEL_ZIP="${MODEL_DIR}.zip"
MODEL_URL="https://alphacephei.com/vosk/models/${MODEL_ZIP}"

echo "=== termiSign Setup ==="
echo ""

echo "[1/4] Criando virtualenv..."
if [ -d "$VENV_DIR" ]; then
    echo "Virtualenv ja existe."
else
    python3 -m venv "$VENV_DIR"
    echo "OK"
fi

PIP="$VENV_DIR/bin/pip"
PYTHON="$VENV_DIR/bin/python3"

echo ""
echo "[2/4] Instalando dependencias Python..."
"$PIP" install -q -r "$SCRIPT_DIR/requirements.txt"
echo "OK"

echo ""
echo "[3/4] Baixando modelo Vosk PT-BR (31MB)..."
cd "$SCRIPT_DIR"
if [ -d "$MODEL_DIR" ]; then
    echo "Modelo ja existe, pulando download."
else
    wget -q --show-progress -O "$MODEL_ZIP" "$MODEL_URL"
    unzip -qo "$MODEL_ZIP"
    rm -f "$MODEL_ZIP"
    echo "OK"
fi

echo ""
echo "[4/4] Verificando microfone..."
"$PYTHON" -c "
import sounddevice as sd
devices = sd.query_devices()
input_devices = [d for d in devices if d['max_input_channels'] > 0]
if input_devices:
    print(f'Microfone encontrado: {input_devices[0][\"name\"]}')
else:
    print('AVISO: Nenhum microfone encontrado!')
"

echo ""
echo "=== Setup completo! ==="
echo "Execute: $VENV_DIR/bin/python3 main.py"
