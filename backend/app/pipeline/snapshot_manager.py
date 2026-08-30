import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)

class SnapshotManager:
    """
    Manages JSON snapshots of scraped content on disk.
    Architecture reference: §5.3 (Filesystem Snapshots)
    """

    def __init__(self):
        self.snapshot_dir = Path(settings.SNAPSHOT_DIR)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _get_url_dir(self, source_url_id: int) -> Path:
        """Returns the directory for a specific source URL ID."""
        url_dir = self.snapshot_dir / str(source_url_id)
        url_dir.mkdir(parents=True, exist_ok=True)
        return url_dir

    def get_current(self, source_url_id: int) -> Any:
        """Reads and returns current.json if it exists."""
        url_dir = self._get_url_dir(source_url_id)
        current_path = url_dir / "current.json"
        if current_path.exists():
            try:
                with open(current_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading current.json for source {source_url_id}: {e}")
        return None

    def save_current(self, source_url_id: int, extracted_data: Dict[str, Any]):
        """Saves extracted data as current.json."""
        url_dir = self._get_url_dir(source_url_id)
        current_path = url_dir / "current.json"
        
        with open(current_path, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=2, default=str)
            
        logger.debug(f"Saved current.json for source_url_id {source_url_id}")

    def rotate(self, source_url_id: int):
        """Moves current.json to previous.json."""
        url_dir = self._get_url_dir(source_url_id)
        current_path = url_dir / "current.json"
        previous_path = url_dir / "previous.json"
        
        if current_path.exists():
            shutil.copy2(current_path, previous_path)
            logger.debug(f"Rotated current.json to previous.json for source_url_id {source_url_id}")

    def compute_diff(self, source_url_id: int):
        """
        Computes a simplistic diff between current.json and previous.json
        and saves it to diff.json.
        """
        url_dir = self._get_url_dir(source_url_id)
        current_path = url_dir / "current.json"
        previous_path = url_dir / "previous.json"
        diff_path = url_dir / "diff.json"
        
        if not current_path.exists() or not previous_path.exists():
            return
            
        try:
            with open(current_path, "r", encoding="utf-8") as fc:
                current_data = json.load(fc)
            with open(previous_path, "r", encoding="utf-8") as fp:
                previous_data = json.load(fp)
                
            # Basic diff logic: just track top-level changes (can be expanded)
            diff = {
                "added": {},
                "removed": {},
                "changed": {}
            }
            
            # This is a very rudimentary diff. For deeper dict diffing, we'd use dictdiffer or deepdiff.
            for k, v in current_data.items():
                if k not in previous_data:
                    diff["added"][k] = v
                elif previous_data[k] != v:
                    diff["changed"][k] = {"old": previous_data[k], "new": v}
                    
            for k, v in previous_data.items():
                if k not in current_data:
                    diff["removed"][k] = v
                    
            with open(diff_path, "w", encoding="utf-8") as fd:
                json.dump(diff, fd, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error computing diff for source_url_id {source_url_id}: {e}")

    def get_diff(self, source_url_id: int) -> Dict[str, Any]:
        """Reads and returns diff.json."""
        url_dir = self._get_url_dir(source_url_id)
        diff_path = url_dir / "diff.json"
        
        if diff_path.exists():
            with open(diff_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def delete_snapshots(self, source_url_id: int):
        """Removes all snapshots for a URL."""
        url_dir = self.snapshot_dir / str(source_url_id)
        if url_dir.exists():
            shutil.rmtree(url_dir)
            logger.info(f"Deleted snapshots for source_url_id {source_url_id}")

snapshot_manager = SnapshotManager()
