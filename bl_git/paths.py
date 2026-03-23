from pathlib import Path

from ..branding import BRAND_SLUG


CANONICAL_NAMESPACE = f".{BRAND_SLUG}"

CANONICAL_BLOCKS_PREFIX = f"{CANONICAL_NAMESPACE}/blocks/"
CANONICAL_MANIFEST_REL = f"{CANONICAL_NAMESPACE}/manifest.json"


def namespace_roots(root: Path):
    return root / CANONICAL_NAMESPACE


def block_relpath(uuid: str, namespace: str = CANONICAL_NAMESPACE):
    return f"{namespace}/blocks/{uuid}.json"


def manifest_relpath(namespace: str = CANONICAL_NAMESPACE):
    return f"{namespace}/manifest.json"


def extract_block_uuid(path: str):
    if not path:
        return None
    if path.startswith(CANONICAL_BLOCKS_PREFIX) and path.endswith(".json"):
        try:
            return Path(path).stem
        except Exception:
            return None
    return None
