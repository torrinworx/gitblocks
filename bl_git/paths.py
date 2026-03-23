from pathlib import Path

from ..branding import BRAND_SLUG, LEGACY_BRAND_SLUG


CANONICAL_NAMESPACE = f".{BRAND_SLUG}"
LEGACY_NAMESPACE = f".{LEGACY_BRAND_SLUG}"

CANONICAL_BLOCKS_PREFIX = f"{CANONICAL_NAMESPACE}/blocks/"
LEGACY_BLOCKS_PREFIX = f"{LEGACY_NAMESPACE}/blocks/"
CANONICAL_MANIFEST_REL = f"{CANONICAL_NAMESPACE}/manifest.json"
LEGACY_MANIFEST_REL = f"{LEGACY_NAMESPACE}/manifest.json"


def namespace_roots(root: Path):
    return root / CANONICAL_NAMESPACE, root / LEGACY_NAMESPACE


def block_relpath(uuid: str, namespace: str = CANONICAL_NAMESPACE):
    return f"{namespace}/blocks/{uuid}.json"


def manifest_relpath(namespace: str = CANONICAL_NAMESPACE):
    return f"{namespace}/manifest.json"


def extract_block_uuid(path: str):
    if not path:
        return None
    for prefix in (CANONICAL_BLOCKS_PREFIX, LEGACY_BLOCKS_PREFIX):
        if path.startswith(prefix) and path.endswith(".json"):
            try:
                return Path(path).stem
            except Exception:
                return None
    return None
