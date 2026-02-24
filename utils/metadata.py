import json
import os
import logging
from typing import Dict, Any, Optional

import utils.constants as constants
from utils.tools import resource_path

logger = logging.getLogger(__name__)

class ChannelMetadata:
    _instance = None
    _data: Dict[str, Dict[str, Any]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChannelMetadata, cls).__new__(cls)
            cls._instance.load()
        return cls._instance

    def load(self):
        """
        Load channel metadata from config/channels.json
        Structure:
        {
            "CCTV-1": {
                "logo": "http://...",
                "epg_id": "cctv1",
                "group": "CCTV",
                "name": "CCTV-1 综合"
            },
            ...
        }
        """
        metadata_path = resource_path("config/channels.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                logger.info(f"Loaded metadata for {len(self._data)} channels from {metadata_path}")
            except Exception as e:
                logger.error(f"Failed to load channel metadata: {e}")
                self._data = {}
        else:
            self._data = {}

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a channel by name.
        """
        return self._data.get(name)

    def get_logo(self, name: str) -> Optional[str]:
        return self._data.get(name, {}).get("logo")

    def get_epg_id(self, name: str) -> Optional[str]:
        return self._data.get(name, {}).get("epg_id")

    def get_group(self, name: str) -> Optional[str]:
        return self._data.get(name, {}).get("group")

channel_metadata = ChannelMetadata()
