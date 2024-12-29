from __future__ import annotations
from datetime import datetime, timedelta
import struct, zlib, sys

def u32(i : int) -> bytes:
    return struct.pack("L", i)

def parse_u16(i : bytes) -> int:
    return struct.unpack("H", i)[0]

def parse_u32(i : bytes) -> int:
    return struct.unpack("L", i)[0]

def parse_cstr(i : bytes) -> str:
    return i[:-1].decode("latin-1") if i[-1] == 0 else i.decode("latin-1")

def parse_str(i) -> str:
    return i if type(i) == str else parse_cstr(i)

def parse_b8(i : bytes) -> str:
    return struct.unpack("?", i)[0]

def parse_u64(i : bytes) -> str:
    return struct.unpack("Q", i)[0]

def parse_steamtime64(b :bytes) -> datetime:
    u64_decoded = parse_u64(b)
    unix = (u64_decoded / 1000000) - 62135596800
    ms = u64_decoded % 1000000
    return datetime.fromtimestamp(unix) + timedelta(milliseconds=ms)

#
# custom steam stuff
#

def parse_dictlist(d : dict) -> list:
    lst = []
    for i,v in d.items():
        if v != b'':
            print("SANITY CHECK FAILED!!!! (appids/parse_list)\n")
            sys.exit()
        lst.append(parse_u32(i))
    return lst

def parse_appicons(d : dict) -> dict:
    if d != {}:
        print("SANITY CHECK FAILED!!!! (appicons)\n")
        print(d)
        sys.exit()
    return d

#
# debug stuff
#

def parse_unimplemented(anything) -> str:
    return "UNIMPLEMENTED!!!"

def parse_passthrough(anything): # for todo things
    return anything

def parse_printonce(anything):
    print(anything)
    sys.exit()

class BaseParser:
    def __getitem__(self, item):
        return self.__dict__[item]
    
    def dict(self):
        return self.__dict__
    
    def __init__(self, b):
        keys = {}
        for k,v in b.items():
            if k == b'__slack__':
                continue
            idx = parse_u32(k)
            if idx in self.parse_map:
                try:
                    keys[self.parse_map[idx][0]] = (self.parse_map[idx][1])(v)
                except Exception as e:
                    print(f"!!!! failed parsing {self.parse_map[idx][0]} id {idx} in {self.__class__.__name__} ({e})")
                    sys.exit()
            else:
                print(f"MISSING PARSER FOR KEY {idx} IN {self.__class__.__name__}")
                sys.exit()
        
        self.__dict__ = keys
        #self.__getitem__ = self.__dict__.__getitem__

class BaseMapParser:
    def __getitem__(self, item):
        return self.__dict__[item]
    
    def dict(self):
        return self.__dict__
    
    
    def __init__(self, b : dict):
        keys = {}
        for k,v in b.items():
            keys[self.parse_map[0](k)] = self.parse_map[1](v)
        self.__dict__ = keys
        #self.__getitem__ = self.__dict__.__getitem__


class UserDefinedRecord(BaseMapParser):
    parse_map = (parse_str, parse_cstr)
    def __init__(self, d : dict):
        super().__init__(d)

class LaunchOptionsRecord(BaseParser):
    parse_map = {
        1 : ("Description", parse_cstr),
        2 : ("CommandLine", parse_cstr),
        3 : ("IconIndex", parse_u32),
        4 : ("NoDesktopShortcut", parse_b8),
        5 : ("NoStartMenuShortcut", parse_b8),
        6 : ("LongRunningUnattended", parse_b8),
        7 : ("ValidOSList", parse_cstr),
    }
    def __init__(self, d : dict):
        super().__init__(d)

class LaunchOptionsRecordList(BaseMapParser):
    parse_map = (parse_u32, LaunchOptionsRecord)
    def __init__(self, d : dict):
        super().__init__(d)

class VersionsRecord(BaseParser):
    parse_map = {
        1 : ("Description", parse_cstr),
        2 : ("VersionId", parse_u32),
        3 : ("IsNotAvailable", parse_b8),
        4 : ("LaunchOptionIdsRecord", parse_dictlist),
        5 : ("DepotEncryptionKey", parse_cstr),
        6 : ("IsEncryptionKeyAvailable", parse_b8),
        7 : ("IsRebased", parse_b8),
        8 : ("IsLongVersionRoll", parse_b8)
    }
    def __init__(self, d : dict):
        super().__init__(d)

class VersionsRecordList(BaseMapParser):
    parse_map = (parse_u32, VersionsRecord)
    def __init__(self, d : dict):
        super().__init__(d)

class FilesystemsRecord(BaseParser):
    parse_map = {
        1 : ("AppId", parse_u32),
        2 : ("MountName", parse_cstr),
        3 : ("IsOptional", parse_b8),
        4 : ("ValidOSList", parse_cstr),
    }
    def __init__(self, d : dict):
        super().__init__(d)

class FilesystemsRecordList(BaseMapParser):
    parse_map = (parse_u32, FilesystemsRecord)
    def __init__(self, d : dict):
        super().__init__(d)

class RegionSpecificRecord(BaseParser):
    parse_map = {
        1 : ("Countries", parse_cstr),
        2 : ("UserDefinedRecord", UserDefinedRecord),
    }
    def __init__(self, d : dict):
        super().__init__(d)
class RegionSpecificRecordList(BaseMapParser):
    parse_map = (parse_u32, RegionSpecificRecord)
    def __init__(self, d : dict):
        super().__init__(d)

class ApplicationRecord(BaseParser):
    parse_map = {
        1 : ("AppId", parse_u32),
        2 : ("Name", parse_cstr),
        3 : ("InstallDirName", parse_cstr),
        4 : ("MinCacheFileSizeMB", parse_u32),
        5 : ("MaxCacheFileSizeMB", parse_u32),
        6 : ("LaunchOptionsRecord", LaunchOptionsRecordList),
        7 : ("AppIconsRecord", parse_appicons),
        8 : ("OnFirstLaunch", parse_u32),
        9 : ("IsBandwidthGreedy", parse_b8),
        10 : ("VersionsRecord", VersionsRecordList),
        11 : ("CurrentVersionId", parse_u32),
        12 : ("FilesystemsRecord", FilesystemsRecordList),
        13 : ("TrickleVersionId", parse_u32),
        14 : ("UserDefinedRecord", UserDefinedRecord),
        15 : ("BetaVersionPassword", parse_cstr),
        16 : ("BetaVersionId", parse_u32),
        17 : ("LegacyInstallDirName", parse_cstr),
        18 : ("SkipMFPOverwrite", parse_b8),
        19 : ("UseFilesystemDvr", parse_b8),
        20 : ("ManifestOnlyApp", parse_b8),
        21 : ("AppOfManifestOnlyCache", parse_u32),
        22 : ("RegionSpecificRecord", RegionSpecificRecordList)
    }
    def __init__(self, d: dict):
        super().__init__(d)

class ApplicationRecordList(BaseMapParser):
    parse_map = (parse_u32, ApplicationRecord)
    def __init__(self, d : dict):
        super().__init__(d)

class DiscountQualifierRecord(BaseParser):
    parse_map = {
        1 : ("Name", parse_cstr),
        2 : ("SubscriptionId", parse_u32)
    }
    def __init__(self, d : dict):
        super().__init__(d)

class DiscountQualifierRecordList(BaseMapParser):
    parse_map = (parse_u32, DiscountQualifierRecord)
    def __init__(self, d : dict):
        super().__init__(d)

class DiscountsRecord(BaseParser):
    parse_map = {
        1 : ("Name", parse_cstr),
        2 : ("DiscountInCents", parse_u32),
        3 : ("DiscountQualifiers", DiscountQualifierRecordList)
    }
    def __init__(self, d : dict):
        super().__init__(d)

class DiscountsRecordList(BaseMapParser):
    parse_map = (parse_u32, DiscountsRecord)
    def __init__(self, d : dict):
        super().__init__(d)

class SubscriptionRecord(BaseParser):
    parse_map = {
        1 : ("SubscriptionId", parse_u32),
        2 : ("Name", parse_cstr),
        3 : ("BillingType", parse_u16),
        4 : ("CostInCents", parse_u32),
        5 : ("PeriodInMinutes", parse_u32),
        6 : ("AppIdsRecord", parse_dictlist),
        7 : ("RunAppId", parse_u32),
        8 : ("OnSubscribeRunLaunchOptionIndex", parse_u32),
        #9 : ("OptionalRateLimitRecord", parse_unimplemented),  # FIX ME FIX ME FIX ME
        10 : ("DiscountsRecord", DiscountsRecordList),
        11 : ("IsPreorder", parse_b8),
        12 : ("RequiresShippingAddress", parse_b8),
        13 : ("DomesticCostInCents", parse_u32),
        14 : ("InternationalCostInCents", parse_u32),
        15 : ("RequiredKeyType", parse_u32),
        16 : ("IsCyberCafe", parse_b8),
        17 : ("GameCode", parse_u32),
        18 : ("GameCodeDescription", parse_cstr),
        19 : ("IsDisabled", parse_b8),
        20 : ("RequiresCD", parse_b8),
        21 : ("TerritoryCode", parse_u32),
        22 : ("IsSteam3Subscription", parse_b8),
        23 : ("ExtendedInfoRecord", UserDefinedRecord)

    }
    def __init__(self, d : dict):
        super().__init__(d)


class SubscriptionRecordList(BaseMapParser):
    parse_map = (parse_u32, SubscriptionRecord)
    def __init__(self, d : dict):
        super().__init__(d)

class AllAppsPublicKeysRecord(BaseMapParser):
    parse_map = (parse_u32, parse_passthrough)
    def __init__(self, d : dict):
        super().__init__(d)

class IndexAppIdToSubscriptionIdsRecord(BaseMapParser):
    parse_map = (parse_u32, parse_dictlist)
    def __init__(self, d : dict):
        super().__init__(d)

    
def blob_unserialize(blobtext : bytes) -> dict:
    if blobtext[0:2] == b"\x01\x43":
        # print("decompress")
        blobtext = zlib.decompress(blobtext[20:])

    blobdict = {}
    (totalsize, slack) = struct.unpack("<LL", blobtext[2:10])

    if slack:
        blobdict[b"__slack__"] = blobtext[-slack:]
    if (totalsize + slack) != len(blobtext):
        raise NameError("Blob not correct length including slack space!")
    index = 10
    while index < totalsize:
        namestart = index + 6
        (namesize, datasize) = struct.unpack("<HL", blobtext[index:namestart])
        datastart = namestart + namesize
        name = blobtext[namestart:datastart]
        dataend = datastart + datasize
        data = blobtext[datastart:dataend]
        if len(data) > 1 and data[0:2] == b"\x01\x50":
            sub_blob = blob_unserialize(data)
            blobdict[name] = sub_blob
        else:
            blobdict[name] = data
        index = index + 6 + namesize + datasize

    return blobdict 

class CDRBlob(BaseParser):
    parse_map = {
        0 : ("VersionNumber", parse_u16),
        1 : ("ApplicationRecord" , ApplicationRecordList),
        2 : ("SubscriptionRecord" , SubscriptionRecordList),
        3 : ("LastChangedExistingAppOrSubscriptionTime" , parse_steamtime64),
        4 : ("IndexAppIdToSubscriptionIdsRecord" , IndexAppIdToSubscriptionIdsRecord),
        5 : ("AllAppsPublicKeysRecord" , AllAppsPublicKeysRecord),
    }
    def __init__(self, d : dict):
        super().__init__(d)
        
    
    @classmethod
    def from_file(self, path :str) -> CDRBlob:
        f = open(path, "rb")
        blob_bin = f.read()
        f.close()
        
        if blob_bin[0:2] == b"\x01\x43" :
            blob_bin = zlib.decompress(blob_bin[20:])
        #print(Blob.blob_unserialize(blob_bin), file=open("dump.txt", "w"))
        unserialized = blob_unserialize(blob_bin)
        if b'TopKey' in unserialized:
            return self(blob_unserialize(unserialized[b'TopKey'][u32(2)][b'ContentDescriptionRecord'][u32(2)]))
        return self(blob_unserialize(blob_bin))
    
