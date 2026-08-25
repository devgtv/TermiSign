from libras.alphabet import ALPHABET

NUMBERS = {
    "0": {
        "pose": "zero_sphere",
        "desc": "Todas as pontas dos dedos juntas formando esfera",
        "duration": 0.8,
    },
    "1": {
        "pose": "one_index",
        "desc": "Indicador estendido pra cima, punho fechado",
        "duration": 0.8,
    },
    "2": {
        "pose": "two_v",
        "desc": "Indicador e medio em V, palma pra fora",
        "duration": 0.8,
    },
    "3": {
        "pose": "three_thumb_v",
        "desc": "Polegar + indicador + medio estendidos",
        "duration": 0.8,
    },
    "4": {
        "pose": "four_fingers",
        "desc": "Quatro dedos estendidos, polegar dobrado",
        "duration": 0.8,
    },
    "5": {
        "pose": "five_open",
        "desc": "Mao aberta, todos os 5 dedos estendidos e separados",
        "duration": 0.8,
    },
    "6": {
        "pose": "six_thumb_index",
        "desc": "Polegar tocando ponta do indicador, 3 dedos estendidos",
        "duration": 0.8,
    },
    "7": {
        "pose": "seven_thumb_ring",
        "desc": "Polegar tocando ponta do anelar, demais estendidos",
        "duration": 0.8,
    },
    "8": {
        "pose": "eight_thumb_middle",
        "desc": "Polegar tocando ponta do medio, demais estendidos",
        "duration": 0.8,
    },
    "9": {
        "pose": "nine_thumb_index_in",
        "desc": "Polegar tocando indicador, palma pra dentro",
        "duration": 0.8,
    },
}


def text_to_libras(text: str) -> list[dict]:
    result = []
    for char in text.lower():
        if char in ALPHABET:
            result.append({"type": "letter", "char": char, **ALPHABET[char]})
        elif char in NUMBERS:
            result.append({"type": "number", "char": char, **NUMBERS[char]})
        elif char == " ":
            result.append({
                "type": "pause",
                "char": " ",
                "pose": "idle",
                "desc": "Pausa entre palavras",
                "duration": 0.4,
            })
    return result
