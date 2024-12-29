from cdr import blob_unserialize, u32
import sys


if not len(sys.argv) > 2:
    print(f"{sys.argv[0]} <second.blob> <output_file.txt>")
    sys.exit()
try:
    f = open(sys.argv[1], "rb")
    dict = blob_unserialize(f.read())
    print(dict, file=open(sys.argv[2], "w"))
except Exception as e:
    print(f"Exception: {e}")