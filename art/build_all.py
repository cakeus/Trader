"""Rebuild every asset: runs each make_*.py in this folder."""
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
failed = []
for script in sorted(glob.glob(os.path.join(HERE, "make_*.py"))):
    name = os.path.basename(script)
    r = subprocess.run([sys.executable, name], cwd=HERE, capture_output=True, text=True)
    print(f"{'ok  ' if r.returncode == 0 else 'FAIL'} {name}")
    if r.returncode:
        failed.append(name)
        print(r.stderr)
sys.exit(1 if failed else 0)
