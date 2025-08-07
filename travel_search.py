# Python
import json
import os
from typing import Dict, Any
import yaml
from inc.flight_graph import FlightGraph
from inc.flights import UserInputFlightsConnector
from inc.connector import Connector
from inc.cache_manager import CacheManager


# TODO: What about intermediate stops? What if I want to fly into frankfurt and then take a train to ghent?
#   I want to be able to route through hubs without having to specify a stop.
# TODO: What about rental cars
# TODO: How to account for overnight travel?
# TODO: How to account for multiple legs of a journey on the same day?

class ConfigLoader:
    """Loads program settings from a YAML config file."""
    CONFIG_FILE = "./config/config.yaml"

    @staticmethod
    def load_config() -> Dict[str, Any]:
        with open(ConfigLoader.CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)


class TravelSearch:
    """Main scraper class that manages connectors and caching."""

    def __init__(self, config: Dict[str, Any]):
        self.connectors = {}
        self.cache_manager = CacheManager(config)

    def register_connector(self, name: str, connector: Connector):
        self.connectors[name] = connector

    def search(self, connector_name: str, origin: str, destination: str, date: str, transportation_mode: str,
               payment_type: str, force_refresh: bool = False) -> Dict[str, Any]:
        # Output cache for debugging
        self.cache_manager.output_cache()

        cache_key = f"{connector_name}_{origin}_{destination}_{date}_{transportation_mode}_{payment_type}"
        if not force_refresh:
            cached_result = self.cache_manager.get_cache(cache_key)
            if cached_result:
                return cached_result

        if connector_name not in self.connectors:
            raise ValueError(f"Connector '{connector_name}' not found.")

        connector = self.connectors[connector_name]
        result = connector.get_details(origin, destination, date, transportation_mode, payment_type)
        self.cache_manager.set_cache(cache_key, result)
        return result


if __name__ == "__main__":
    # Load configuration
    config = ConfigLoader.load_config()
    flights_connector = UserInputFlightsConnector(config)

    # Initialize FlightGraph
    flight_graph = FlightGraph(config["cache_dir"])

    # Output cache for debugging
    cache_manager = CacheManager(config)
    # cache_manager.output_cache()

    # Load cached journey legs into the graph
    for cache_file in os.listdir(config["cache_dir"]):
        if cache_file.endswith(".json"):
            with open(os.path.join(config["cache_dir"], cache_file), "r") as f:
                cached_data = json.load(f)["result"]
                flight_graph.add_leg(cached_data["origin"].upper(), cached_data["destination"].upper(),
                    cached_data["date"], cached_data["price"], cached_data["duration"], cached_data["airline"])

    # Prompt user for origin and destinations
    origin = input("Enter the origin: ").strip().upper()
    destinations = {}
    constraints = {}
    while True:
        destination = input(
            "Enter destination (or type 'done' to finish, or 'const' to enter date constraints): ").strip().upper()
        if destination.lower() == "done":
            break
        if destination.lower() == "const":
            dest = input("Enter the destination with date constraints: ").strip().upper()
            sdate = input(f"Enter a start range for bad dates (inclusive) for {dest} (YYYY-MM-DD): ").strip()
            edate = input(f"Enter an end range for bad dates (inclusive) for {dest} (YYYY-MM-DD): ").strip()
            if dest in constraints:
                constraints[dest].append((sdate, edate))
            else:
                constraints[dest] = [(sdate, edate)]
            continue

        try:
            min_days = int(input(f"Enter the minimum number of days to spend in {destination}: ").strip())
            max_days = int(input(f"Enter the maximum number of days to spend in {destination}: ").strip())
            if min_days > max_days:
                print("Minimum days cannot be greater than maximum days. Please try again.")
                continue
        except ValueError:
            print("Invalid input. Please enter integers for the number of days.")
            continue

        destinations[destination] = (min_days, max_days)

    # Find the least-cost path using A* search
    best_path, best_cost = flight_graph.find_least_cost_path(origin, destinations, constraints)

    # Output results
    print("Round-trip path:")
    for location, date, cost in best_path:
        if date:
            print(f"{location} (Date: {date}, Cost: {cost})")
        else:
            print(location)
    print(f"Total cost: {best_cost}")
