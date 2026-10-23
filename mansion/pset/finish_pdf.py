"""Finish the Mansion PDF; adapted from Claude's finish_pdf.py.
Codex, 2026-10-23: explicit release target/zone, distinct from build dates.
Run after latexmk, or on the checked PDF copied from the pinned source.
"""
import argparse, datetime, glob, os, shutil, subprocess
from pathlib import Path
from zoneinfo import ZoneInfo
import pikepdf

parser = argparse.ArgumentParser()
parser.add_argument("--timezone", default="America/New_York")
parser.add_argument("--release-at", help="ISO datetime with explicit UTC offset")
args = parser.parse_args()
zone = ZoneInfo(args.timezone)
now = datetime.datetime.now(zone)
release = datetime.datetime.fromisoformat(args.release_at) if args.release_at else None
if release is not None:
    if release.tzinfo is None:
        parser.error("--release-at requires an explicit UTC offset")
    if release.utcoffset() != release.astimezone(zone).utcoffset():
        parser.error("--release-at offset does not match --timezone")
    release = release.astimezone(zone)

def pdf_date(value):
    off = value.strftime("%z")
    return value.strftime("D:%Y%m%d%H%M%S") + f"{off[:3]}'{off[3:]}'"

with pikepdf.open("mansion_pset.pdf") as pdf:
    for key in ("/Producer", "/Creator", "/Keywords", "/Trapped"):
        if key in pdf.docinfo:
            del pdf.docinfo[key]
    # Preserve the actual source build date, including its real offset.
    if "/CreationDate" not in pdf.docinfo:
        pdf.docinfo["/CreationDate"] = pdf_date(now)
    pdf.docinfo["/ModDate"] = pdf_date(now)
    if release is not None:
        pdf.docinfo["/ReleaseTarget"] = release.isoformat()
        pdf.docinfo["/ReleaseTimeZone"] = args.timezone
        pdf.docinfo["/ReleaseStatus"] = "Release candidate; target time is not a publication claim."
    name = f"The Mansion that did not Spin {(release or now):%y%m%d%H%M}.pdf"
    pdf.save(name)
print(name)
