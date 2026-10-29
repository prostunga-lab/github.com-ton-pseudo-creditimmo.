"""Génère un Short vertical CréditImmo à partir d'un fichier JSON de scènes.
Usage : python3 make_short.py <scenes.json> [AAAA-MM-JJ]
La vidéo est écrite dans videos/<date>/<slug>.mp4 à la racine du dépôt.
"""
import datetime, json, os, re, subprocess, sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
FPS_LONG = 25
GAP = 0.25  # silence entre deux scènes (s)
# traitement « studio » de la voix : EQ, compression, légère ambiance, volume normalisé YouTube (-14 LUFS)
VOICE_FX = "highpass=f=70,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,aecho=0.85:0.5:25:0.05,loudnorm=I=-14:TP=-1.5"


def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out)


def main(spec_path, day=None):
    day = day or datetime.datetime.now(ZoneInfo("Europe/Brussels")).date().isoformat()
    spec = json.load(open(spec_path))
    work = os.path.join(HERE, "work", spec["slug"])
    os.makedirs(work, exist_ok=True)

    t, words, parts = 0.0, [], []
    for i, sc in enumerate(spec["scenes"]):
        mp3, wj = f"{work}/s{i}.mp3", f"{work}/s{i}.json"
        subprocess.check_call(["python3", f"{HERE}/tts.py", spec["voice"], sc["text"], mp3, wj, spec.get("rate", "+5%")])
        d = dur(mp3)
        sc["start"], sc["end"] = t, t + d
        # captions: drop pure punctuation, group by 3 words, break on punctuation
        chunk, n = len({w.get("chunk") for w in words if "chunk" in w}), 0
        for w in json.load(open(wj)):
            txt = w["w"].strip()
            if not re.search(r"\w", txt):
                continue
            words.append({"w": txt, "s": t + w["s"], "e": t + w["e"], "chunk": chunk})
            n += 1
            if n == 3 or re.search(r"[.,!?…]$", txt):
                chunk, n = chunk + 1, 0
        if n:
            chunk += 1
        parts.append(mp3)
        t += d + GAP
    total = t + 0.6
    for k, w in enumerate(words):
        w["next"] = words[k + 1]["s"] if k + 1 < len(words) else total
        # keep a chunk on screen until the next chunk starts
    spec["words"], spec["total"] = words, total

    # audio: concatenate scenes with gaps
    filt, inputs = "", []
    for i, p in enumerate(parts):
        inputs += ["-i", p]
        filt += f"[{i}:a]apad=pad_dur={GAP}[a{i}];"
    filt += "".join(f"[a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1,apad=pad_dur=0.6,{VOICE_FX}[out]"
    audio = f"{work}/voice.m4a"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", filt, "-map", "[out]", "-c:a", "aac", "-b:a", "160k", audio])

    json.dump(spec, open(f"{work}/data.json", "w"), ensure_ascii=False)
    frames = f"{work}/frames"
    os.makedirs(frames, exist_ok=True)
    fps = FPS_LONG if spec.get("format") == "long" else FPS
    subprocess.check_call(["node", f"{HERE}/render.js", f"{work}/data.json", frames, str(fps), str(total)])

    out_dir = os.path.join(os.path.dirname(HERE), "videos", day)
    os.makedirs(out_dir, exist_ok=True)
    out = f"{out_dir}/{spec['slug']}.mp4"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{frames}/f%05d.jpg", "-i", audio,
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20", "-c:a", "copy", "-shortest", "-movflags", "+faststart", out])
    print(out, f"{total:.1f}s")


main(*sys.argv[1:3])
