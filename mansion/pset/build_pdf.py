"""Run the established XeLaTeX build with honest compile/save timestamps.
Codex (OpenAI), 2026-10-23, for dr. kraemer. No date or filesystem backdating.
"""
import argparse, datetime as dt, json, os, subprocess, time
from pathlib import Path
from zoneinfo import ZoneInfo
import pikepdf

p = argparse.ArgumentParser()
p.add_argument("--final", action="store_true")
p.add_argument("--aim", help="Aware ISO target for creation; one wait, at most 60 seconds")
args = p.parse_args()
root = Path(__file__).resolve().parent
os.chdir(root)
zone = ZoneInfo("America/Los_Angeles")
target = dt.datetime.fromisoformat(args.aim) if args.aim else None
if target is not None and target.tzinfo is None:
    p.error("--aim needs a UTC offset")
clock = lambda: dt.datetime.now(zone)
iso = lambda t: t.isoformat(timespec="microseconds")
def pdfdate(t):
    off = t.strftime("%z")
    return t.strftime("D:%Y%m%d%H%M%S") + f"{off[:3]}'{off[3:]}'"
env = os.environ.copy()
deps = root.parent / "build-through/tex-deps/usr/share/texlive/texmf-dist/tex"
if deps.exists():
    env["TEXINPUTS"] = str(deps) + "//:" + env.get("TEXINPUTS", "")
compile_started = clock()
shown = compile_started.strftime("%Y-%m-%d %H:%M:%S") + f".{compile_started.microsecond // 10000:02d} " + compile_started.tzname()
Path("build_stamp.tex").write_text(r"\newcommand{\BuildStamp}{" + shown + "}\n")
with open("build.log", "w") as log:
    subprocess.run(["latexmk", "-xelatex", "-interaction=nonstopmode",
                    "-halt-on-error", "mansion_pset.tex"],
                   env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
compile_completed = clock()
with pikepdf.open("mansion_pset.pdf") as pdf:
    for key in ("/Producer", "/Creator", "/Keywords", "/Trapped"):
        if key in pdf.docinfo:
            del pdf.docinfo[key]
    if "/CreationDate" in pdf.docinfo:
        pdf.docinfo["/RawCompilerCreationDate"] = str(pdf.docinfo["/CreationDate"])
    pdf.docinfo["/CompilationStarted"] = iso(compile_started)
    pdf.docinfo["/CompilationCompleted"] = iso(compile_completed)
    pdf.docinfo["/TimeZone"] = "America/Los_Angeles"
    pdf.docinfo["/ReleaseStatus"] = "Final edition" if args.final else "Review copy"
    if target is not None:
        pdf.docinfo["/TargetCreationTime"] = iso(target.astimezone(zone))
        delay = (target - clock()).total_seconds()
        if delay > 60:
            raise SystemExit("Target is over 60 seconds away; invoke the build nearer the target.")
        if delay > 0:
            time.sleep(delay)
    created = clock()
    stamp = created.strftime("%Y%m%d%H%M%S") + f"{created.microsecond // 10000:02d}"
    name = f"The_Mansion_that_did_not_Spin_{stamp}.pdf"
    pdf.docinfo["/CreationDate"] = pdfdate(created)
    pdf.docinfo["/ModDate"] = pdfdate(created)
    pdf.docinfo["/ActualCreationTime"] = iso(created)
    if target is not None:
        pdf.docinfo["/CreationOffsetSeconds"] = str((created-target).total_seconds())
    pdf.save(name)
saved = clock()
record = {"file":name, "compiled_display":shown,
          "compile_started":iso(compile_started), "compile_completed":iso(compile_completed),
          "creation":iso(created), "saved":iso(saved),
          "target":iso(target) if target is not None else None}
Path("build_record.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))

