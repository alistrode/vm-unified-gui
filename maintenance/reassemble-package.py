#!/usr/bin/env python3
"""Join existing-files ZIP parts without modifying the recorded machine files.
Run from the repository: python3 maintenance/reassemble-package.py
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
parts=sorted((root/'release').glob('Ubuntu-MultiContainer-GUI-B-existing-files.zip.part*'))
if not parts:raise SystemExit('No package parts found')
out=root/'release/Ubuntu-MultiContainer-GUI-B-existing-files.zip'
with out.open('wb') as dst:
 for part in parts:
  with part.open('rb') as src:
   while data:=src.read(1024*1024):dst.write(data)
print(out)
