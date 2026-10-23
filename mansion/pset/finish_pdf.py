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
parser.add_argument("--final", action="store_true", help="Mark the saved edition final, rather than a candidate")
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
    # This is a new PDF edition. xdvipdfmx can emit a wrong zone; don't
    # carry that into its creation date. Retain the input's stamp as provenance.
    if "/CreationDate" in pdf.docinfo and "/SourceCreationDate" not in pdf.docinfo:
        pdf.docinfo["/SourceCreationDate"] = str(pdf.docinfo["/CreationDate"])
    if release is not None:
        pdf.docinfo["/ReleaseTarget"] = release.isoformat()
        pdf.docinfo["/ReleaseTimeZone"] = args.timezone
        pdf.docinfo["/ReleaseStatus"] = ("Final edition" if args.final else
            "Release candidate; target time is not a publication claim.")
    name = f"The Mansion that did not Spin {(release or now):%y%m%d%H%M}.pdf"
    created = datetime.datetime.now(zone)
    pdf.docinfo["/CreationDate"] = pdf_date(created)
    pdf.docinfo["/ModDate"] = pdf_date(created)
    pdf.docinfo["/ActualCreationTime"] = created.isoformat(timespec="microseconds")
    pdf.save(name)
print(name)

