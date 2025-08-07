# Python
import json
import os
import time
from typing import Dict, Any


class CacheManager:

    def __init__(self, config: Dict[str, Any]):
        self.cache_dir = config["cache_dir"]
        self.cache_timeout = config["cache_timeout"]
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_cache(self, key: str) -> Dict[str, Any]:
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                data = json.load(f)
                if time.time() - data["timestamp"] < self.cache_timeout:
                    return data["result"]
        return None

    def set_cache(self, key: str, result: Dict[str, Any]):
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        with open(cache_file, "w") as f:
            json.dump({"timestamp": time.time(), "result": result}, f)

    def output_cache(self):
        """Outputs the full cache for debugging."""
        print("Cache contents:")
        for cache_file in os.listdir(self.cache_dir):
            if cache_file.endswith(".json"):
                with open(os.path.join(self.cache_dir, cache_file), "r") as f:
                    cached_data = json.load(f)
                    print(json.dumps(cached_data, indent=4))
