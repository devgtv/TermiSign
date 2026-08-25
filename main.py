#!/usr/bin/env python3
"""termiSign - Traducao de Audio para LIBRAS via Terminal"""

import argparse
import logging
import signal
import sys
import time

import curses

from audio.capture import AudioCapture
from stt.recognizer import SpeechRecognizer
from libras.numbers import text_to_libras
from animation.renderer import Renderer

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("termisign")


def parse_args():
    parser = argparse.ArgumentParser(
        description="termiSign - Transcreve audio e traduz para LIBRAS no terminal"
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
  Traducao de Audio para LIBRAS via Terminal
    """
    print(banner)


def main_loop(stdscr, args):
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
    round_num = 0

    try:
        while listening:
            round_num += 1
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


def main():
    args = parse_args()

    if args.debug:
        logging.getLogger("termisign").setLevel(logging.DEBUG)

    print_banner()
    print("Pressione Q a qualquer momento para sair.")
    print("Iniciando em 2 segundos...")
    time.sleep(2)

    try:
        curses.wrapper(lambda stdscr: main_loop(stdscr, args))
    except KeyboardInterrupt:
        pass
    finally:
        print("\nObrigado por usar o termiSign!")


if __name__ == "__main__":
    main()
