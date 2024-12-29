from cdr import CDRBlob
import sys
if len(sys.argv) < 2:
    print(f"{sys.argv[0]} <secondblob> <appid>")
    sys.exit()

b = Blob.from_file(sys.argv[1])
appid = int(sys.argv[2])
for k,v in b.ApplicationRecord[appid].FilesystemsRecord.dict().items():
    print(f'{v.AppId} v{b.ApplicationRecord[v.AppId].CurrentVersionId} ({b.ApplicationRecord[v.AppId].Name}) { "" if v.IsOptional else "not"} optional os {"any/all" if not "ValidOSList" in v.dict() else v.ValidOSList}')