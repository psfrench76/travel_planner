#!/usr/bin/env python3
import unittest
from scraper import CacheManager, ExpediaFlightsConnector, Scraper

class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.config = {"cache_dir": "./test_cache", "cache_timeout": 10}
        self.cache_manager = CacheManager(self.config)

    def test_cache_set_and_get(self):
        self.cache_manager.set_cache("test_key", {"data": "test"})
        result = self.cache_manager.get_cache("test_key")
        self.assertEqual(result, {"data": "test"})

class TestExpediaFlightsConnector(unittest.TestCase):
    def setUp(self):
        self.config = {"connectors": {"expedia_flights": {"base_url": "https://example.com"}}}
        self.connector = ExpediaFlightsConnector(self.config)

    def test_search(self):
        result = self.connector.search("JFK", "LAX", "2023-12-01", "flight", "money")
        self.assertEqual(result["flight_number"], "123")

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
        self.scraper = Scraper(self.config)
        self.connector = ExpediaFlightsConnector(self.config)
        self.scraper.register_connector("expedia_flights", self.connector)

    def test_search_with_cache(self):
        self.scraper.cache_manager.set_cache(
            "expedia_flights_JFK_LAX_2023-12-01_flight_money",
            {"data": "cached"}
        )
        result = self.scraper.search(
            "expedia_flights", "JFK", "LAX", "2023-12-01", "flight", "money", force_refresh=False
        )
        self.assertEqual(result, {"data": "cached"})

if __name__ == "__main__":
    unittest.main()