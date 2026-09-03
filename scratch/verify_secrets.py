import os
import re

SUSPICIOUS_PATTERNS = [
    ("gsk_ literal", r"gsk_[A-Za-z0-9]{20,}"),
    ("sk- literal", r"sk-[A-Za-z0-9]{20,}"),
    ("AIza literal", r"AIza[0-9A-Za-z-_]{35}"),
    ("Private Key marker", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

root_dir = "."
found_issues = []

for dirpath, dirnames, filenames in os.walk(root_dir):
    # skip .git and node_modules
    if any(p in dirpath for p in [".git", "node_modules", ".gemini", "__pycache__"]):
        continue
    for fname in filenames:
        fpath = os.path.join(dirpath, fname)
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for label, pat in SUSPICIOUS_PATTERNS:
                    if re.search(pat, content):
                        found_issues.append((fpath, label))
        except Exception:
            pass

print("=== REPOSITORY SECRET SCAN RESULTS ===")
if found_issues:
    print(f"FAILED: Found {len(found_issues)} suspicious patterns:")
    for path, label in found_issues:
        print(f"  - {path}: {label}")
else:
    print("PASS: Zero secret patterns or credential literals found in active working tree.")
