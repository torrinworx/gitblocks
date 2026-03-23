# Blender Data Block Serialization
This library is courtesy of [Swann Martinez](https://gitlab.com/slumber), extracted from his Blender add-on [multi-user](https://gitlab.com/slumber/multi-user/-/tree/master/multi_user/bl_types?ref_type=heads).

The goal of pulling this out into its own library is to make an independent Blender data block serialization library so that Blender data blocks can be stored, transmitted, and modified in a way that is serializable and deserializable back into a `.blend` file. This library can support far more advanced applications and manipulations of data blocks.

Right now, `bl_types` runs on its own without any dependencies. Slumber's original implementation used a Python library written for replicating data called [replication](https://gitlab.com/slumber/replication), powering the multi-user add-on. `bl_types` uses a couple of classes to define methods for each `bl_type`, plus a few helpers from the replication library, so those pieces were extracted into `/bl_types/replicate`.

Some `deepdiff`-powered features are disabled for now. For GitBlocks and its data-block Git workflow, that functionality is not currently needed, but the commented code remains so the library can grow without losing the original implementation notes.

# Usage
The `bl_types` library provides a standardized way to **serialize**, **deserialize**, and **sync** Blender data blocks (objects, cameras, materials, scenes, etc.) between different states or even external systems. It allows tools like GitBlocks to treat Blender data as structured data suitable for version control and remote collaboration.

The system revolves around two key classes:

- [`DataTranslationProtocol`](./replication/protocol.py)  
  Handles registration, lookup, and dispatch of all Blender datablock serialization logic.
- [`ReplicatedDatablock`](./replication/protocol.py)  
  Provides the abstract base class for every data block implementation (e.g., `BlCamera`, `BlObject`, etc.), defining how a Blender datablock is constructed, dumped, and reloaded.

## Quick Start

**1. Import and get the protocol**
```python
import bl_types

bpy_protocol = bl_types.get_data_translation_protocol()
```

This returns an initialized `DataTranslationProtocol` object, with all Blender data type modules registered (`bl_camera`, `bl_scene`, `bl_mesh`, etc.).

---

**2. Serializing Blender datablocks**
```python
camera = bpy.data.cameras["Camera"]
data = bpy_protocol.dump(camera)

print(data["name"], data["lens"], data["clip_start"])
```

This creates a `dict` representing a complete snapshot of the current Blender data block for JSON serialization, diffing, or transmitting.

---

**3. Reconstruct a datablock from serialized data**
```python
import json

# pretend `data` comes from a manifest or file
json_path = "/path/to/.blocks/<uuid>.json"
with open(json_path, "r") as f:
    data = json.load(f)

datablock = bpy_protocol.construct(data)
```

If you already have a corresponding datablock in Blender, you can load updates directly into it:
```python
datablock = bpy.data.cameras["Camera"]
bpy_protocol.load(data, datablock)
```

---

**4. Resolve existing datablocks and dependencies**

```python
# Find an existing data block by uuid or metadata
datablock = bpy_protocol.resolve(data)

# Retrieve dependent data-blocks (e.g., images used by camera backgrounds)
deps = bpy_protocol.resolve_deps(datablock)
```

---

**5. Writing to or reading from disk**

Because the data is json serializable, you can persist datablocks as independent `.json` files for each Blender datablock:

```python
import json, os

output_path = os.path.join(".blocks", f"{datablock.name}.json")
with open(output_path, "w") as f:
    json.dump(bpy_protocol.dump(datablock), f, indent=2)
```

To restore:

```python
with open(output_path, "r") as f:
    data = json.load(f)
restored = bpy_protocol.construct(data)
```

---


# Protocol (Data Block Classes)
Each supported Blender data type is implemented as a class that inherits from `ReplicatedDatablock`.  
The protocol ensures that **every data block type** follows the same interface, making them safely interchangeable in the serialization pipeline.

#### **Required Methods**
| Method | Description |
| ------- | ------------ |
| `construct(data: dict) -> bpy.types.ID` | Creates a new datablock in Blender using the provided serialized data (called when restoring a data block). |
| `dump(datablock: bpy.types.ID) -> dict` | Serializes a Blender datablock into a dictionary representation. |
| `load(data: dict, datablock: bpy.types.ID)` | Updates an existing datablock with the provided serialized data. |
| `resolve(data: dict) -> bpy.types.ID or None` | Attempts to find a corresponding datablock in Blender (e.g., by UUID or name). |
| `resolve_deps(datablock: bpy.types.ID) -> list[bpy.types.ID]` | Returns a list of other datablocks that this one depends on (images, actions, etc.). |

#### **Optional Methods**
These are not fully implemented in all bl_types, so they are not universally useful like the methods above.

| Method | Description |
| ------- | ------------ |
| `needs_update(datablock, data) -> bool` | Allows for a "fast-check" to see if a datablock and its serialized state differ. Default always returns True. |
| `compute_delta(last_data, current_data) -> Delta` | (optional, requires `DeepDiff`) Calculate a structural diff between two serialized versions. Currently disabled in extracted version. |


#### **Meta Attributes**
Each `ReplicatedDatablock` subclass also defines a few metadata attributes:

| Attribute | Description |
| ---------- | ------------ |
| `bl_id` | The corresponding `bpy.data` collection name (`"cameras"`, `"objects"`, `"materials"`, etc.). |
| `bl_class` | The native `bpy.types` class for that datablock (e.g. `bpy.types.Camera`). |
| `bl_icon` | (optional) Used for UI display of the block. |
| `use_delta` | Controls if delta changes are supported. |
| `_type` | Defines the target `bpy.types` for registration (`bpy.types.Camera`). |
| `_class` | The class implementing it (e.g. `BlCamera`). |

#### **Registration**
All bl_types are added to the `__all__` list inside `__init__.py`:

```python
__all__ = [
    'bl_object',
    'bl_mesh',
    'bl_camera',
    'bl_light',
    ...
]
```

They are automatically imported and registered when `get_data_translation_protocol()` is called.

---

### **How the Protocol Works**

1. `get_data_translation_protocol()`  
   Instantiates a `DataTranslationProtocol` object and imports all `bl_*` modules.

2. Each module registers itself using:
   ```python
   _type = bpy.types.Camera
   _class = BlCamera
   ```
   The protocol maps this native Blender type name to its implementation class. (This can probably be converted to a less maintenance burden singlton auto class registration pattern for simplicity of the child classes.)

3. All supported data types are stored in:
   ```python
   bpy_protocol.implementations
   ```

4. The protocol dispatches calls based on the datablock’s actual Blender type during operations like `dump()`, `construct()`, etc.

---

# Caveats
As stated in the multi-user main README, there are several data blocks that aren't fully supported yet:

multi-user roadmap/board has multiple issues that I would like to keept rack of here or work on myself:  
https://gitlab.com/slumber/multi-user/-/boards/929107

greese pencils stroke:  
https://gitlab.com/slumber/multi-user/-/issues/149

particle support:  
https://gitlab.com/slumber/multi-user/-/issues/24


speaker sound sync: (think this is something multi user needs to worry about, for the purposes of this bl_types library we don't care)  
https://gitlab.com/slumber/multi-user/-/issues/65


Another thing to note for GitBlocks is that we only check the data blocks in the class list, so we never have to worry about an unsupported data block crashing the system; updates are driven by the list provided by `implementations.items()`.
