#!/usr/bin/env python3
import unittest
import yaml
from unittest.mock import patch
from travel_search import CacheManager, UserInputFlightsConnector, TravelSearch

class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.config = {"cache_dir": "./test_cache", "cache_timeout": 10}
        self.cache_manager = CacheManager(self.config)

    def test_cache_set_and_get(self):
        self.cache_manager.set_cache("test_key", {"data": "test"})
        result = self.cache_manager.get_cache("test_key")
        self.assertEqual(result, {"data": "test"})

class TestUserInputFlightsConnector(unittest.TestCase):
    def setUp(self):
        self.config = {
            "connectors": {"expedia_flights": {"base_url": "https://example.com"}},
            "airlines": {
                "Alaska": "AS",
                "Delta": "DL",
                "United": "UA",
                "Frontier": "F9",
                "Spirit": "NK",
                "British Airways": "BA"
            }
        }
        self.connector = UserInputFlightsConnector(self.config)

    def test_parse_price(self):
        self.assertEqual(self.connector.parse_price("100"), 100.0)
        self.assertEqual(self.connector.parse_price("$200.50"), 200.5)
        with self.assertRaises(ValueError):
            self.connector.parse_price("invalid")

    def test_parse_duration(self):
        self.assertEqual(self.connector.parse_duration("2:30"), "2:30")
        self.assertEqual(self.connector.parse_duration("2h 45m"), "2:45")
        self.assertEqual(self.connector.parse_duration("1 hour 15 minutes"), "1:15")
        with self.assertRaises(ValueError):
            self.connector.parse_duration("invalid")

    def test_match_airline(self):
        self.assertEqual(self.connector.match_airline("AS"), "Alaska")
        self.assertEqual(self.connector.match_airline("Delta"), "Delta")
        self.assertEqual(self.connector.match_airline("british airways"), "British Airways")
        with self.assertRaises(ValueError):
            self.connector.match_airline("Unknown Airline")

    @patch("builtins.input", side_effect=["100", "2:30", "Delta"])
    def test_search(self, mock_input):
        result = self.connector.search("JFK", "LAX", "2023-12-01", "flight", "money")
        self.assertEqual(result["price"], 100.0)
        self.assertEqual(result["duration"], "2:30")
        self.assertEqual(result["airline"], "Delta")

if __name__ == "__main__":
    unittest.main()

class TestScraper(unittest.TestCase):
    def setUp(self):
        self.config = {
            "cache_dir": "./test_cache",
            "cache_timeout": 10,
            "connectors": {
                "expedia_flights": {
                    "base_url": "https://example.com"
                }
            }
        }
        self.travel_search = TravelSearch(self.config)
        self.connector = UserInputFlightsConnector(self.config)
        self.travel_search.register_connector("expedia_flights", self.connector)

    def test_search_with_cache(self):
        self.travel_search.cache_manager.set_cache(
            "expedia_flights_JFK_LAX_2023-12-01_flight_money",
            {"data": "cached"}
        )
        result = self.travel_search.search(
            "expedia_flights", "JFK", "LAX", "2023-12-01", "flight", "money", force_refresh=False
        )
        self.assertEqual(result, {"data": "cached"})

class TestConfigFile(unittest.TestCase):
    def setUp(self):
        self.config_file = './config/config.yaml'
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def test_airlines_exist(self):
        self.assertIn('airlines', self.config, "Airlines key is missing in config.")
        self.assertIsInstance(self.config['airlines'], dict, "Airlines should be a dictionary.")

    def test_airlines_valid(self):
        airlines = self.config['airlines']
        for name, abbreviation in airlines.items():
            self.assertIsInstance(name, str, "Airline name should be a string.")
            self.assertIsInstance(abbreviation, str, "Airline abbreviation should be a string.")
            self.assertEqual(len(abbreviation), 2, "Airline abbreviation should be two letters.")

    def test_connectors_exist(self):
        self.assertIn('connectors', self.config, "Connectors key is missing in config.")
        self.assertIsInstance(self.config['connectors'], dict, "Connectors should be a dictionary.")

if __name__ == "__main__":
    unittest.main()