import json
import os
import traceback

from .json_io import default_json_decoder, serialize_json_data
from .paths import block_relpath


class BlocksMixin:
    def _delete_block_file(self, cozystudio_uuid):
        try:
            block_file = self.blockspath / f"{cozystudio_uuid}.json"
            if not block_file.exists():
                print(f"[BpyGit] Block file not found: {block_file}")
                return False
            block_file.unlink()
            print(f"[BpyGit] Deleted block file: {block_file}")
            return True
        except Exception as e:
            print(f"[BpyGit] Error deleting block file '{cozystudio_uuid}': {e}")
            print(traceback.format_exc())
            return False

    def _write_block_file(self, cozystudio_uuid, block_str):
        block_path = os.path.join(self.blockspath, f"{cozystudio_uuid}.json")
        try:
            with open(block_path, "w") as f:
                f.write(block_str)
        except Exception:
            print(traceback.format_exc())
            print(block_str)

    def _read(self, cozystudio_uuid):
        for block_path in (
            self.blockspath / f"{cozystudio_uuid}.json",
            self.legacy_blockspath / f"{cozystudio_uuid}.json",
        ):
            if block_path.exists():
                with open(block_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data = default_json_decoder(data)
                return data
        raise FileNotFoundError(f"Data file not found: {self.blockspath / f'{cozystudio_uuid}.json'}")

    def _load_block_data(self, ref, uuid):
        if ref == "WORKING_TREE":
            for block_dir in (self.blockspath, self.legacy_blockspath):
                block_path = block_dir / f"{uuid}.json"
                if block_path.exists():
                    with open(block_path, "r", encoding="utf-8") as handle:
                        return default_json_decoder(json.load(handle))
            return None

        if not ref:
            return None

        for block_rel in (block_relpath(uuid), block_relpath(uuid, namespace=".cozystudio")):
            try:
                raw = self.repo.git.show(f"{ref}:{block_rel}")
                return default_json_decoder(json.loads(raw))
            except Exception:
                continue
        return None

    def _write_merged_blocks(self, merged_blocks):
        existing = {
            path.stem
            for path in self.blockspath.iterdir()
            if path.is_file() and path.name.endswith(".json")
        }

        for uuid in existing:
            if uuid not in merged_blocks:
                self._delete_block_file(uuid)

        for uuid, data in merged_blocks.items():
            serialized = serialize_json_data(data)
            self._write_block_file(uuid, serialized)
