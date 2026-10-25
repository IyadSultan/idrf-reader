"""Optional second image source: DICOM studies in Azure Blob Storage, laid out as
<container>/<prefix>/<patient>/<study>/<series>/<files>.

The coordinator picks studies in the coordinator page. Each picked study becomes a case whose folder is the
study's full location, <container>/<prefix>/<patient>/<study>. Its files are downloaded to a temporary folder
only while its volume is prepared, then deleted again.

Settings: AZURE_STORAGE_CONNECTION_STRING (account key or SAS) and AZURE_STORAGE_SOURCES, a comma-separated
list of container/prefix pairs such as "cnsimaging/cnsimaging, nb2015/nb2015". AZURE_STORAGE_CONTAINER with
AZURE_STORAGE_PREFIX still work for a single source.
"""
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import config  # noqa: F401  (loads .env before settings are read)

# Files stored next to the DICOMs that are never images to import
SKIP_EXT = {".jpg", ".jpeg", ".png", ".gif", ".json", ".html", ".htm", ".i16", ".txt", ".xml", ".pdf", ".csv"}

_clients = {}


def sources():
    """[(container, prefix)] with prefix empty or ending in '/'."""
    raw = os.environ.get("AZURE_STORAGE_SOURCES", "").strip()
    if not raw:
        raw = "/".join(x for x in (os.environ.get("AZURE_STORAGE_CONTAINER", "").strip(),
                                   os.environ.get("AZURE_STORAGE_PREFIX", "").strip().strip("/")) if x)
    out = []
    for item in re.split(r"[,;\s]+", raw):
        container, _, pfx = item.strip().strip("/").partition("/")
        if container:
            out.append((container.lower(), pfx.strip("/") + "/" if pfx.strip("/") else ""))
    return out


def enabled():
    return bool(os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "").strip()) and bool(sources())


def where():
    return [f"{c}/{p}".rstrip("/") for c, p in sources()]


def container(name):
    if name not in _clients:
        from azure.storage.blob import ContainerClient
        _clients[name] = ContainerClient.from_connection_string(
            os.environ["AZURE_STORAGE_CONNECTION_STRING"].strip(), name)
    return _clients[name]


def legacy_folder(folder):
    """Cases added before several sources were supported stored only <patient>/<study> of the first source."""
    if folder.count("/") != 1 or not sources():
        return None
    c, p = sources()[0]
    return f"{c}/{p}{folder}"


def _subfolders(cc, pfx):
    return sorted(b.name[len(pfx):].rstrip("/") for b in cc.walk_blobs(name_starts_with=pfx, delimiter="/")
                  if b.name.endswith("/"))


def list_studies():
    """Every <patient>/<study> folder under each source."""
    out = []
    with ThreadPoolExecutor(32) as ex:
        for c, pfx in sources():
            cc = container(c)
            patients = _subfolders(cc, pfx)
            studies = ex.map(lambda p: _subfolders(cc, f"{pfx}{p}/"), patients)
            source = f"{c}/{pfx}".rstrip("/")
            out += [{"path": f"{c}/{pfx}{p}/{s}", "source": source, "patient": p, "study": s}
                    for p, ss in zip(patients, studies) for s in ss]
    return out


def _split(path):
    c, _, rest = path.strip("/").partition("/")
    return container(c), rest + "/"


def study_files(path):
    cc, base = _split(path)
    return [b for b in cc.list_blobs(name_starts_with=base)
            if os.path.splitext(b.name)[1].lower() not in SKIP_EXT and not b.name.endswith("/")]


def signature(files):
    return "blob:{}:{}:{}".format(len(files), sum(b.size for b in files),
                                  int(max(b.last_modified.timestamp() for b in files)))


def download(path, files, dest):
    """Download a study's files into dest, keeping the series subfolders. Returns the total bytes."""
    cc, base = _split(path)
    dest = Path(dest).resolve()

    def get(b):
        p = (dest / b.name[len(base):]).resolve()
        if dest not in p.parents:
            return
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            cc.download_blob(b.name, max_concurrency=2).readinto(f)

    with ThreadPoolExecutor(16) as ex:
        list(ex.map(get, files))
    return sum(b.size for b in files)
