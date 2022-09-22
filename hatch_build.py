from pathlib import Path
from typing import Any
from typing import Dict

from hatchling.metadata.plugin.interface import MetadataHookInterface


class ReadmeMetadataHook(MetadataHookInterface):
    def update(self, metadata: Dict[str, Any]) -> None:
        readme = Path(self.root, "README.md").read_text()
        changes = Path(self.root, "CHANGES.md").read_text()

        metadata["readme"] = {
            "content-type": "text/markdown",
            "text": "\n".join([readme, changes]),
        }
