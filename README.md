# termiSign

Transcricao de audio para LIBRAS via terminal com animacao 3D ASCII.

## O que faz

1. **Captura audio** do microfone em tempo real
2. **Transcreve fala** para texto (Google online + Vosk offline)
3. **Traduz texto** para sinais LIBRAS (alfabeto + numeros)
4. **Anima boneco ASCII 3D** mostrando cada letra/numero sinalizado

## Requisitos

- Python 3.10+
- Microfone conectado
- Linux (testado), macOS, Windows

## Instalacao

```bash
chmod +x setup.sh
./setup.sh
```

Isso cria um virtualenv, instala dependencias e baixa o modelo Vosk PT-BR (31MB).

## Uso

```bash
# Com virtualenv
.venv/bin/python3 main.py

# Modo offline apenas
.venv/bin/python3 main.py --offline

# Tempo de escuta maior
.venv/bin/python3 main.py --listen-time 8

# Debug
.venv/bin/python3 main.py --debug
```

## Atalhos

- **Q** — Sair do programa

## Arquitetura

```
termiSign/
├── main.py                 # CLI entry point
├── audio/
│   └── capture.py          # sounddevice — captura de microfone
├── stt/
│   ├── google_stt.py       # Google STT free tier (online)
│   ├── vosk_stt.py         # Vosk offline PT-BR
│   └── recognizer.py       # Interface unificada online/offline
├── libras/
│   ├── alphabet.py         # Mapeamento A-Z → poses
│   └── numbers.py          # Mapeamento 0-9 → poses + text_to_libras()
├── animation/
│   ├── poses.py            # 42 poses ASCII art (26 letras + 10 numeros + idle + animacoes)
│   ├── renderer.py         # Renderer curses com cores ANSI
│   └── transition.py       # Interpolacao entre poses
├── requirements.txt
├── setup.sh
└── README.md
```

## Fluxo

```
Microfone → [sounddevice] → audio raw
         → [Google STT / Vosk] → texto "Obrigado"
         → [text_to_libras] → ["O","B","R","I","G","A","D","O"]
         → [poses ASCII] → sequencia de frames
         → [curses renderer] → boneco 3D animado no terminal
```

## STT

- **Online**: Google STT free tier (requer internet, mais preciso)
- **Offline**: Vosk com modelo PT-BR (31MB, sem internet)
- Fallback automatico: tenta Google primeiro, se falhar usa Vosk

## LIBRAS

- 26 letras do alfabeto (datilologia)
- 10 numeros (0-9)
- Letras dinamicas (H, J, K, X, Y, Z) com frames de animacao de movimento
- 42 poses ASCII art no total
