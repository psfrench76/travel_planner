import json
import os
import time
from typing import Dict, Any
import yaml
from inc.flights import UserInputFlightsConnector
from inc.connector import Connector
import argparse

#TODO - deal with baggage requirements. Should build into queries and have costs in settings

class ConfigLoader:
    """Loads program settings from a YAML config file."""
    CONFIG_FILE = "./config/config.yaml"

    @staticmethod
    def load_config() -> Dict[str, Any]:
        with open(ConfigLoader.CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)

class QueryLoader:
    """Loads query settings from a YAML config file."""
    QUERY_FILE = "./query/default.yaml"

    @staticmethod
    def load_query() -> Dict[str, Any]:
        with open(QueryLoader.QUERY_FILE, "r") as f:
            return yaml.safe_load(f)

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




class TravelSearch:
    """Main scraper class that manages connectors and caching."""
    def __init__(self, config: Dict[str, Any]):
        self.connectors = {}
        self.cache_manager = CacheManager(config)

    def register_connector(self, name: str, connector: Connector):
        self.connectors[name] = connector

    def search(self, connector_name: str, origin: str, destination: str, date: str, transportation_mode: str, payment_type: str, force_refresh: bool = False) -> Dict[str, Any]:
        cache_key = f"{connector_name}_{origin}_{destination}_{date}_{transportation_mode}_{payment_type}"
        if not force_refresh:
            cached_result = self.cache_manager.get_cache(cache_key)
            if cached_result:
                return cached_result

        if connector_name not in self.connectors:
            raise ValueError(f"Connector '{connector_name}' not found.")

        connector = self.connectors[connector_name]
        result = connector.search(origin, destination, date, transportation_mode, payment_type)
        self.cache_manager.set_cache(cache_key, result)
        return result


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Travel planning app")
    parser.add_argument("--force-refresh", "-f", action="store_true", help="Force cache refresh for queries")
    args = parser.parse_args()

    # Load configuration and query
    config = ConfigLoader.load_config()
    query = QueryLoader.load_query()

    # Initialize scraper and connector
    scraper = TravelSearch(config)
    flights_connector = UserInputFlightsConnector(config)
    scraper.register_connector("flights_connector", flights_connector)

    # Perform search with the force-refresh flag
    result = scraper.search(
        "flights_connector",
        query["origin"],
        query["destination"],
        query["date_range"]["start"],
        "flight",  # Transportation mode
        "money",   # Payment type
        force_refresh=args.force_refresh
    )
    print(result)