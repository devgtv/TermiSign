# termiSign

Transcricao de audio para LIBRAS com avatar 3D em tempo real.

## O que faz

1. **Captura audio** do microfone em tempo real
2. **Transcreve fala** para texto (Google online + Vosk offline)
3. **Traduz texto** para sinais LIBRAS (alfabeto + numeros)
4. **Anima avatar 3D** com OpenGL mostrando cada letra/numero sinalizado

## Renderizacao

- **3D (default)**: Janela OpenGL com boneco 3D articulado, lighting Phong, camera orbital
- **ASCII**: Fallback terminal com curses para ambientes sem suporte grafico

## Requisitos

- Python 3.10+
- Microfone conectado
- Para modo 3D: OpenGL 2.1+, display grafico
- Linux (testado), macOS, Windows

## Instalacao

```bash
chmod +x setup.sh
./setup.sh
```

Isso cria um virtualenv, instala dependencias e baixa o modelo Vosk PT-BR (31MB).

## Uso

```bash
# Modo 3D (default)
.venv/bin/python3 main.py

# Modo ASCII terminal
.venv/bin/python3 main.py --renderer ascii

# Modo offline apenas
.venv/bin/python3 main.py --offline

# Janela maior
.venv/bin/python3 main.py --width 1024 --height 768

# Tempo de escuta maior
.venv/bin/python3 main.py --listen-time 8

# Debug
.venv/bin/python3 main.py --debug
```

## Atalhos (modo 3D)

- **R** — Liga/desliga rotacao automatica
- **ESC / Q** — Sair

## Atalhos (modo ASCII)

- **Q** — Sair

## Arquitetura

```
termiSign/
├── main.py                     # CLI entry point (3D + ASCII)
├── audio/
│   └── capture.py              # sounddevice — captura de microfone
├── stt/
│   ├── google_stt.py           # Google STT free tier (online)
│   ├── vosk_stt.py             # Vosk offline PT-BR
│   └── recognizer.py           # Interface unificada online/offline
├── libras/
│   ├── alphabet.py             # Mapeamento A-Z → poses
│   └── numbers.py              # Mapeamento 0-9 → poses + text_to_libras()
├── animation/
│   ├── model3d.py              # Modelo 3D parametrico (OpenGL)
│   │                           #   - Corpo: esferas + cilindros
│   │                           #   - Maos articuladas: 5 dedos independentes
│   │                           #   - 37 poses 3D mapeadas
│   ├── renderer_3d.py          # Renderer OpenGL (pygame + PyOpenGL)
│   │                           #   - Lighting Phong (2 luzes)
│   │                           #   - Camera orbital
│   │                           #   - Transicoes suaves entre poses
│   │                           #   - Overlay 2D para texto
│   ├── poses.py                # 42 poses ASCII art (fallback)
│   ├── renderer.py             # Renderer curses (fallback)
│   └── transition.py           # Interpolacao ASCII
├── requirements.txt
├── setup.sh
└── README.md
```

## Fluxo

```
Microfone → [sounddevice] → audio raw
         → [Google STT / Vosk] → texto
         → [text_to_libras] → sequencia de sinais
         → [3D model] → poses interpoladas
         → [OpenGL renderer] → avatar 3D animado na janela
```

## STT

- **Online**: Google STT free tier (requer internet, mais preciso)
- **Offline**: Vosk com modelo PT-BR (31MB, sem internet)
- Fallback automatico: tenta Google primeiro, se falhar usa Vosk

## LIBRAS

- 26 letras do alfabeto (datilologia)
- 10 numeros (0-9)
- 37 poses 3D com articulacao de dedos
- Transicoes suaves com interpolação easing

## Modelo 3D

- Corpo: cabeca (esfera), torso (cilindro taper), bracos e pernas (capsulas)
- Maos: 5 dedos articulados (indicador, medio, anelar, mindinho, polegar)
- Parametros: angulo de ombro/cotovelo/pulso, spread dos dedos, flexao individual
- Iluminacao: 2 luzes (principal + preenchimento), Phong shading
- Camera: orbital com rotacao automatica
