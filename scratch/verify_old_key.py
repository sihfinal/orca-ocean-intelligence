import os
import hashlib

# SHA-256 hash of the exposed key to test without exposing the plaintext key
TARGET_HASH = "fa70fc601726a978f8cb08696ec02c84a5658e3eb9996944e05b5ee2dc730245"

found = False
for dirpath, dirnames, filenames in os.walk("."):
    if any(p in dirpath for p in [".git", "node_modules", ".gemini", "__pycache__"]):
        continue
    for fname in filenames:
        fpath = os.path.join(dirpath, fname)
        try:
            with open(fpath, "rb") as f:
                content = f.read()
                # Check sliding window or token check
                for word in content.split():
                    if hashlib.sha256(word).hexdigest() == TARGET_HASH:
                        found = True
                        break
        except Exception:
            pass

if found:
    print("Previously exposed Groq credential: STILL PRESENT")
else:
    print("Previously exposed Groq credential: NOT PRESENT")
