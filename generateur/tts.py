"""Synthèse vocale (edge-tts) avec horodatage mot à mot.
Usage : python3 tts.py <voix> <texte> <sortie.mp3> <sortie_mots.json> [débit, ex. +0%]
"""
import asyncio, json, ssl, sys

_orig = ssl.create_default_context
def _ctx(*a, **k):
    c = _orig(*a, **k)
    c.load_verify_locations("/root/.ccr/ca-bundle.crt")
    return c
ssl.create_default_context = _ctx

import edge_tts


async def main(voice, text, out_mp3, out_json, rate="+10%"):
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words = []
    with open(out_mp3, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "w": chunk["text"],
                    "s": chunk["offset"] / 1e7,
                    "e": (chunk["offset"] + chunk["duration"]) / 1e7,
                })
    with open(out_json, "w") as f:
        json.dump(words, f, ensure_ascii=False)


asyncio.run(main(*sys.argv[1:6]))
