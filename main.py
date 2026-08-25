#!/usr/bin/env python3
"""termiSign - Traducao de Audio para LIBRAS via Terminal"""

import argparse
import logging
import os
import sys
import time

from audio.capture import AudioCapture
from stt.recognizer import SpeechRecognizer
from libras.numbers import text_to_libras

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("termisign")


def parse_args():
    parser = argparse.ArgumentParser(
        description="termiSign - Transcreve audio e traduz para LIBRAS"
    )
    parser.add_argument(
        "--renderer",
        choices=["3d", "ascii"],
        default="3d",
        help="Renderer: 3d (OpenGL/janela) ou ascii (terminal curses) (default: 3d)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Forca modo offline (Vosk) apenas",
    )
    parser.add_argument(
        "--model",
        default="vosk-model-small-pt-0.3",
        help="Caminho do modelo Vosk (default: vosk-model-small-pt-0.3)",
    )
    parser.add_argument(
        "--listen-time",
        type=float,
        default=5.0,
        help="Tempo de escuta por rodada em segundos (default: 5)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=800,
        help="Largura da janela 3D (default: 800)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=600,
        help="Altura da janela 3D (default: 600)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Ativa logging detalhado",
    )
    return parser.parse_args()


def print_banner():
    banner = r"""
  _____ ____    _                         _
 |_   _/ ___|  / \   __ _  ___ _ __   __| |
   | || |     / _ \ / _` |/ _ \ '_ \ / _` |
   | || |___ / ___ \ (_| |  __/ | | | (_| |
   |_| \____/_/   \_\__, |\___|_| |_|\__,_|
                     |___/
  Traducao de Audio para LIBRAS
    """
    print(banner)


def run_3d(args):
    try:
        from animation.renderer_3d import Renderer3D
    except ImportError as e:
        print(f"Erro ao importar renderer 3D: {e}")
        print("Instale as dependencias: pip install pygame PyOpenGL")
        sys.exit(1)

    renderer = Renderer3D(width=args.width, height=args.height)
    audio = AudioCapture()
    recognizer = SpeechRecognizer(args.model)

    if args.offline:
        recognizer.force_offline()

    logger.info(f"Modo STT: {recognizer.mode}")
    audio.start()

    listening = True

    try:
        while listening:
            if not renderer.run_idle():
                break

            chunks = []
            start = time.time()

            while time.time() - start < args.listen_time:
                chunk = audio.get_chunk(timeout=0.1)
                if chunk:
                    chunks.append(chunk)
                if not renderer.run_idle():
                    listening = False
                    break

            if not listening:
                break

            if not chunks:
                continue

            audio_data = b"".join(chunks)
            text = recognizer.transcribe(audio_data)

            if text:
                signs = text_to_libras(text)
                if signs:
                    if not renderer.animate_sequence(signs):
                        break
            else:
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        audio.stop()
        renderer.cleanup()


def run_ascii(args):
    import curses
    from animation.renderer import Renderer

    def main_loop(stdscr):
        renderer = Renderer(stdscr)
        audio = AudioCapture()
        recognizer = SpeechRecognizer(args.model)

        if args.offline:
            recognizer.force_offline()

        renderer.render_idle()
        time.sleep(1)
        audio.start()
        logger.info(f"Modo STT: {recognizer.mode}")

        listening = True
        try:
            while listening:
                chunks = []
                start = time.time()

                while time.time() - start < args.listen_time:
                    chunk = audio.get_chunk(timeout=0.5)
                    if chunk:
                        chunks.append(chunk)
                    key = stdscr.getch()
                    if key == ord("q"):
                        listening = False
                        break
                    renderer.render_idle()

                if not listening:
                    break
                if not chunks:
                    continue

                audio_data = b"".join(chunks)
                text = recognizer.transcribe(audio_data)

                if text:
                    signs = text_to_libras(text)
                    if signs:
                        if not renderer.animate_sequence(signs):
                            break
                else:
                    time.sleep(0.3)
        except KeyboardInterrupt:
            pass
        finally:
            audio.stop()

    try:
        curses.wrapper(lambda stdscr: main_loop(stdscr))
    except KeyboardInterrupt:
        pass


def main():
    args = parse_args()

    if args.debug:
        logging.getLogger("termisign").setLevel(logging.DEBUG)

    print_banner()

    if args.renderer == "3d":
        print("Modo: Renderizacao 3D (OpenGL)")
        print("Controles: [R] Rotacionar | [ESC/Q] Sair")
        print("Iniciando...")
        time.sleep(1)
        run_3d(args)
    else:
        print("Modo: ASCII Terminal (curses)")
        print("Pressione Q a qualquer momento para sair.")
        print("Iniciando em 2 segundos...")
        time.sleep(2)
        run_ascii(args)

    print("\nObrigado por usar o termiSign!")


if __name__ == "__main__":
    main()
