from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import icu
from jamdict import Jamdict
from pykakasi import kakasi
from unidecode import unidecode

_YOON: Dict[str, str] = {
    # palatalized combinations
    "kya": "キャ",
    "kyu": "キュ",
    "kyo": "キョ",
    "gya": "ギャ",
    "gyu": "ギュ",
    "gyo": "ギョ",
    "sha": "シャ",
    "shu": "シュ",
    "sho": "ショ",
    "ja": "ジャ",
    "ju": "ジュ",
    "jo": "ジョ",
    "jya": "ジャ",
    "jyu": "ジュ",
    "jyo": "ジョ",
    "cha": "チャ",
    "chu": "チュ",
    "cho": "チョ",
    "nya": "ニャ",
    "nyu": "ニュ",
    "nyo": "ニョ",
    "hya": "ヒャ",
    "hyu": "ヒュ",
    "hyo": "ヒョ",
    "bya": "ビャ",
    "byu": "ビュ",
    "byo": "ビョ",
    "pya": "ピャ",
    "pyu": "ピュ",
    "pyo": "ピョ",
    "mya": "ミャ",
    "myu": "ミュ",
    "myo": "ミョ",
    "rya": "リャ",
    "ryu": "リュ",
    "ryo": "リョ",
}

_SPECIAL: Dict[str, str] = {
    "shi": "シ",
    "chi": "チ",
    "tsu": "ツ",
    "fu": "フ",
    "ji": "ジ",
    "ti": "チ",
    "tu": "ツ",
    "di": "ディ",
    "du": "ドゥ",
    "wi": "ウィ",
    "we": "ウェ",
    "wu": "ウ",
    "va": "ヴァ",
    "vi": "ヴィ",
    "vu": "ヴ",
    "ve": "ヴェ",
    "vo": "ヴォ",
    "fa": "ファ",
    "fi": "フィ",
    "fe": "フェ",
    "fo": "フォ",
}

_BASE: Dict[str, Dict[str, str]] = {
    "": {"a": "ア", "i": "イ", "u": "ウ", "e": "エ", "o": "オ"},
    "k": {"a": "カ", "i": "キ", "u": "ク", "e": "ケ", "o": "コ"},
    "g": {"a": "ガ", "i": "ギ", "u": "グ", "e": "ゲ", "o": "ゴ"},
    "s": {"a": "サ", "i": "シ", "u": "ス", "e": "セ", "o": "ソ"},
    "z": {"a": "ザ", "i": "ジ", "u": "ズ", "e": "ゼ", "o": "ゾ"},
    "t": {"a": "タ", "i": "チ", "u": "ツ", "e": "テ", "o": "ト"},
    "d": {"a": "ダ", "i": "ヂ", "u": "ヅ", "e": "デ", "o": "ド"},
    "n": {"a": "ナ", "i": "ニ", "u": "ヌ", "e": "ネ", "o": "ノ"},
    "h": {"a": "ハ", "i": "ヒ", "u": "フ", "e": "ヘ", "o": "ホ"},
    "b": {"a": "バ", "i": "ビ", "u": "ブ", "e": "ベ", "o": "ボ"},
    "p": {"a": "パ", "i": "ピ", "u": "プ", "e": "ペ", "o": "ポ"},
    "m": {"a": "マ", "i": "ミ", "u": "ム", "e": "メ", "o": "モ"},
    "y": {"a": "ヤ", "i": "イ", "u": "ユ", "e": "イェ", "o": "ヨ"},
    "r": {"a": "ラ", "i": "リ", "u": "ル", "e": "レ", "o": "ロ"},
    "w": {"a": "ワ", "i": "ウィ", "u": "ウ", "e": "ウェ", "o": "ヲ"},
    "j": {"a": "ジャ", "i": "ジ", "u": "ジュ", "e": "ジェ", "o": "ジョ"},
    "q": {"a": "クァ", "i": "クィ", "u": "ク", "e": "クェ", "o": "クォ"},
    "x": {"a": "ザ", "i": "クスィ", "u": "クス", "e": "グゼ", "o": "クソ"},
    "c": {"a": "カ", "i": "シ", "u": "ク", "e": "セ", "o": "コ"},
    "v": {"a": "ヴァ", "i": "ヴィ", "u": "ヴ", "e": "ヴェ", "o": "ヴォ"},
}


def _long_vowelize(kata: str) -> str:
    result = []
    for ch in kata:
        if result and ch in {"ア", "イ", "ウ", "エ", "オ"} and result[-1] == ch:
            result.append("ー")
        else:
            result.append(ch)
    return "".join(result)


def _romaji_to_katakana(token: str) -> str:
    s = token.lower()
    out = []
    i = 0
    while i < len(s):
        # sokuon (double consonant except 'n')
        if (
            i + 1 < len(s)
            and s[i] == s[i + 1]
            and s[i].isalpha()
            and s[i] not in {"a", "i", "u", "e", "o", "n"}
        ):
            out.append("ッ")
            i += 1
            continue

        # terminal or standalone 'n' → ン
        if s[i] == "n":
            nxt = s[i + 1] if i + 1 < len(s) else ""
            if not nxt or nxt not in {"a", "i", "u", "e", "o", "y"}:
                out.append("ン")
                i += 1
                continue

        # yoon combos (3 letters)
        if i + 2 < len(s):
            tri = s[i : i + 3]
            if tri in _YOON:
                out.append(_YOON[tri])
                i += 3
                continue

        # specials (2-3 letters)
        if i + 2 <= len(s):
            for length in (3, 2):
                if i + length <= len(s):
                    seg = s[i : i + length]
                    if seg in _SPECIAL:
                        out.append(_SPECIAL[seg])
                        i += length
                        break
            else:
                pass
            if i > 0 and out and out[-1] in _SPECIAL.values():
                continue

        # base CV or V
        c = ""
        v = ""
        if i < len(s) and s[i] in _BASE:
            c = s[i]
            if i + 1 < len(s) and s[i + 1] in {"a", "i", "u", "e", "o"}:
                v = s[i + 1]
                out.append(_BASE[c][v])
                i += 2
                continue
            else:
                # bare consonant, approximate with vowel 'u'
                out.append(
                    _BASE[c]["u"]
                )  # e.g., 't' -> トゥ (approx via ツ/トゥ), keep simple ル/ム style
                i += 1
                continue
        # vowel only
        if s[i] in {"a", "i", "u", "e", "o"}:
            out.append(_BASE[""][s[i]])
            i += 1
            continue

        # non-letter: skip
        i += 1

    return _long_vowelize("".join(out))


# --- Normalization rules ---------------------------------------------------

_OLD_KANA_MAP: Dict[str, str] = {
    "ヷ": "ヴァ",
    "ヸ": "ヴィ",
    "ヹ": "ヴェ",
    "ヺ": "ヴォ",
}


def _normalize_katakana_after_icu(kata: str, latin_query: str) -> str:
    # Replace archaic kana with modern ヴ + vowel
    for old, new in _OLD_KANA_MAP.items():
        kata = kata.replace(old, new)

    # Heuristics for Russian endings commonly used in names
    lower = latin_query.lower()
    # -ina → リーナ
    if lower.endswith("ina") and kata.endswith("リナ"):
        kata = kata[:-2] + "リーナ"
    # -iy / -ii → long i (イー) at the end
    if (lower.endswith("iy") or lower.endswith("ii")) and kata.endswith("イ"):
        kata = kata[:-1] + "イー"
    # -ey → エイ at the end
    if lower.endswith("ey") and kata.endswith("エ"):
        kata = kata + "イ"

    return kata


# --- Exceptions ------------------------------------------------------------

_EXCEPTIONS: Dict[str, Tuple[str, str]] = {
    # Common Russian names with preferred forms
    "nikita": ("ニキータ", "Nikita"),
    "evelina": ("エヴェリーナ", "Everina"),
    "dmitriy": ("ドミトリー", "Dmitriy"),
    "dmitri": ("ドミトリー", "Dmitri"),
    "sergey": ("セルゲイ", "Sergei"),
    "sergei": ("セルゲイ", "Sergei"),
    "alexey": ("アレクセイ", "Alexey"),
    "aleksei": ("アレクセイ", "Aleksei"),
    "mikhail": ("ミハイル", "Mikhail"),
    "yuliya": ("ユーリヤ", "Yuliya"),
    "julia": ("ユリア", "Julia"),
    "maria": ("マリヤ", "Mariya"),
}


def _exceptions_lookup(name: str) -> Optional[Tuple[str, str]]:
    key = unidecode(name).strip().lower()
    return _EXCEPTIONS.get(key)


# --- ICU helpers -----------------------------------------------------------


def _icu_ru_to_latin(text: str) -> str:
    if icu is None:
        return unidecode(text)
    try:
        tr = icu.Transliterator.createInstance("Russian-Latin/BGN")
        return tr.transliterate(text)
    except Exception:
        return unidecode(text)


def _icu_latin_to_katakana(text: str) -> Optional[str]:
    if icu is None:
        return None
    try:
        tr = icu.Transliterator.createInstance("Latin-Katakana")
        return tr.transliterate(text)
    except Exception:
        return None


# --- jamdict lookup -------------------------------------------------------

_jamdict_instance: Any | None = None


def _get_jamdict() -> Any | None:
    global _jamdict_instance
    if Jamdict is None:
        return None
    if _jamdict_instance is None:
        try:
            _jamdict_instance = Jamdict()
        except Exception:
            _jamdict_instance = None
    return _jamdict_instance


def _lookup_katakana_in_jamdict(query: str) -> Optional[str]:
    jd = _get_jamdict()
    if jd is None:
        return None
    try:
        res = jd.lookup(query)
    except Exception:
        return None

    # Prefer name entries (JMnedict)
    names = getattr(res, "names", None) or getattr(res, "name_entries", None) or []
    for ne in names:  # type: ignore[assignment]
        r_list = getattr(ne, "r_ele", [])
        for r in r_list:
            reading = getattr(r, "reb", None)
            if not reading:
                continue
            # Ensure Katakana; if Hiragana, keep as-is (later we can convert if needed)
            return reading
    return None


def convert_name(name: str) -> Tuple[str, str]:
    ascii_name = unidecode(name).strip()
    if not ascii_name:
        return ("", "")

    # 0) Exceptions
    exc = _exceptions_lookup(name)
    if exc:
        return exc

    # 1) Try JMnedict by romanized query (BGN)
    latin_query = _icu_ru_to_latin(name).strip() or ascii_name
    kata_from_dict = _lookup_katakana_in_jamdict(latin_query)
    if kata_from_dict:
        kata = kata_from_dict
        # normalize to Katakana if needed
        try:
            import jaconv  # local import to avoid hard dep if unused

            kata = jaconv.hira2kata(kata)
        except Exception:
            pass
        kk = kakasi()
        kk.setMode("H", "a")
        kk.setMode("K", "a")
        kk.setMode("J", "a")
        conv = kk.getConverter()
        romaji = conv.do(kata)
        return kata, romaji.capitalize()

    # 2) Fallback via ICU Latin→Katakana if available
    icu_kata = _icu_latin_to_katakana(latin_query)
    if icu_kata:
        icu_kata = _normalize_katakana_after_icu(icu_kata, latin_query)
        kk = kakasi()
        kk.setMode("H", "a")
        kk.setMode("K", "a")
        kk.setMode("J", "a")
        conv = kk.getConverter()
        romaji = conv.do(icu_kata)
        return icu_kata, romaji.capitalize()

    # 3) Final fallback: heuristic mapper
    tokens = [t for t in ascii_name.replace("-", " ").split() if t]
    kata_tokens = [_romaji_to_katakana(t) for t in tokens]
    katakana = " ".join(kata_tokens)

    # Canonical romaji from resulting katakana (Hepburn-ish)
    kk = kakasi()
    kk.setMode("H", "a")
    kk.setMode("K", "a")
    kk.setMode("J", "a")
    conv = kk.getConverter()
    romaji = " ".join(conv.do(k) for k in kata_tokens) if kata_tokens else ""

    return katakana, romaji.capitalize()
