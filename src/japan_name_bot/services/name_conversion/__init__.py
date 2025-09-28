from __future__ import annotations

from typing import Tuple

import jaconv
from pykakasi import kakasi
from unidecode import unidecode


def convert_name_offline(name: str) -> Tuple[str, str]:
    normalized = unidecode(name).strip()
    if not normalized:
        return ("", "")

    # naive romaji normalization
    romaji = normalized

    # convert romaji->hiragana (pykakasi expects kana/kanji input, but we can
    # round-trip via kakasi romaji conversion for a consistent romaji output)
    kk = kakasi()
    kk.setMode("H", "a")  # hira->ascii
    kk.setMode("K", "a")  # kata->ascii
    kk.setMode("J", "a")  # kanji->ascii
    conv = kk.getConverter()
    romaji_canonical = conv.do(romaji)

    # build katakana from romaji_canonical heuristically: using jaconv.hira2kata
    # pykakasi can produce romaji from kana/kanji, but not vice versa reliably.
    # For MVP: if input already ascii, expose katakana as uppercase ascii placeholder.
    # Later we can refine to a proper romaji->kana mapping.
    katakana = jaconv.hira2kata(romaji_canonical)
    if katakana == romaji_canonical:
        katakana = romaji_canonical.upper()

    return katakana, romaji_canonical
