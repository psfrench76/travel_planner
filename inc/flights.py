from .connector import Connector
from typing import Dict, Any
import re
from datetime import timedelta, datetime
import difflib

class UserInputFlightsConnector(Connector):
    def __init__(self, config):
        self.airlines = config["airlines"]

    def get_details(self, origin: str, destination: str, date: str, transportation_mode: str="flight", payment_type: str="money") -> Dict[str, Any]:
        if transportation_mode != "flight":
            raise ValueError("ExpediaFlightsConnector only supports flights.")

        print(f"Please enter flight details for the following search:")
        print(f"Origin: {origin}, Destination: {destination}, Date: {date}, Payment Type: {payment_type}")

        price_input = input("Enter the price of the flight: ")
        #duration_input = input("Enter the duration of the flight: ")
        #airline_input = input("Enter the airline name or abbreviation: ")
        duration_input = "1h"
        airline_input = "Alaska"

        price = self.parse_price(price_input)
        duration = self.parse_duration(duration_input)
        airline = self.match_airline(airline_input)

        return {
            "price": price,
            "duration": duration,
            "airline": airline
        }

    def get_price(self, origin: str, destination: str, date: str):
        price_input = input(f"Enter the price of the flight for date {date.strftime("%Y-%m-%d")}: (or type 'done' to exit calendar mode): ")
        if price_input.lower() == "done":
            return None
        return self.parse_price(price_input)

    def match_airline(self, airline_input: str) -> str:
        """Matches the airline input to the dictionary or suggests the closest match."""
        airline_input_lower = airline_input.lower()

        # Check if input matches abbreviation
        for name, abbreviation in self.airlines.items():
            if airline_input_upper := airline_input.upper() == abbreviation:
                return name

        # Check if input matches full name (case-insensitive)
        for name in self.airlines.keys():
            if airline_input_lower == name.lower():
                return name

        # Suggest closest match (case-insensitive)
        closest_match = difflib.get_close_matches(airline_input_lower, [name.lower() for name in self.airlines.keys()], n=1)
        if closest_match:
            original_name = next(name for name in self.airlines.keys() if name.lower() == closest_match[0])
            confirmation = input(f"Did you mean '{original_name}'? (y/n): ").strip().lower()
            if confirmation == "y":
                return original_name

        raise ValueError("Airline not recognized.")

    def parse_duration(self, duration_input: str) -> str:
        """Parses the duration input into a standardized format (HH:MM)."""
        hh_mm_match = re.match(r"^(\d{1,2}):(\d{2})$", duration_input)
        if hh_mm_match:
            hours = int(hh_mm_match.group(1))
            minutes = int(hh_mm_match.group(2))
        else:
            hours_match = re.search(r"(\d+)\s*(h|hour|hours)", duration_input, re.IGNORECASE)
            minutes_match = re.search(r"(\d+)\s*(m|min|minute|minutes)", duration_input, re.IGNORECASE)

            if not hours_match and not minutes_match:
                raise ValueError("Invalid duration format.")

            hours = int(hours_match.group(1)) if hours_match else 0
            minutes = int(minutes_match.group(1)) if minutes_match else 0

        total_duration = timedelta(hours=hours, minutes=minutes)
        return f"{total_duration.seconds // 3600}:{(total_duration.seconds // 60) % 60:02}"

    def parse_price(self, price_input: str) -> float:
        """Parses the price input into a float."""
        price_match = re.search(r"(\d+(\.\d+)?)", price_input)
        if not price_match:
            raise ValueError("Invalid price format.")
        return float(price_match.group(1))