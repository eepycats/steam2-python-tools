from cdr import blob_unserialize, u32
import sys


if not len(sys.argv) > 2:
    print(f"{sys.argv[0]} <ClientRegistry.blob> <output_file.bin>")
    sys.exit()
try:
    f = open(sys.argv[1], "rb")
    dict = blob_unserialize(f.read())
    fout = open(sys.argv[2], "wb")
    fout.write(dict[b'TopKey'][u32(2)][b'ContentDescriptionRecord'][u32(2)])
except Exception as e:
    print(f"Exception: {e}")