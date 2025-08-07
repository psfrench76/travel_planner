# Python
from inc.cache_manager import CacheManager
from inc.flights import UserInputFlightsConnector
from travel_search import ConfigLoader
from datetime import datetime, timedelta


def main():
    # Load configuration from config.yaml
    config = ConfigLoader.load_config()

    # Initialize CacheManager and FlightsConnector
    cache_manager = CacheManager(config)
    flights_connector = UserInputFlightsConnector(config)
    in_cal = False
    transportation_mode = "flight"
    payment_type = "money"

    while True:
        # Prompt user for flight details
        if not in_cal:
            origin = input("Enter the origin airport code (or type 'done' to finish): ").strip().upper()
            if origin.lower() == "done":
                break

            destination = input("Enter the destination airport code: ").strip().upper()
            date = input("Enter the flight date (YYYY-MM-DD): (or 'cal' to enter calendar of fares) ").strip()

            if date.lower() == "cal":
                date = input("Enter the start date for calendar of fares (YYYY-MM-DD): ").strip()
                date = datetime.strptime(date, "%Y-%m-%d")
                in_cal = True
            else:
                # Validate date format
                try:
                    date = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
                    continue
        else:
            date = date + timedelta(days=1)

        # Get flight details using the connector
        try:
            if in_cal:
                # Handle calendar of fares logic here
                price = flights_connector.get_price(origin, destination, date)
                if price is None:
                    print("Exiting calendar mode.")
                    in_cal = False
                    continue
                flight_details = {"price": price, "duration": "1h",  # Duration not available in calendar mode
                    "airline": "Delta"  # Airline not available in calendar mode
                }
            else:
                flight_details = flights_connector.get_details(origin, destination, date, transportation_mode,
                                                               payment_type)
        except ValueError as e:
            print(f"Error: {e}")
            continue

        # Generate cache key
        cache_key = f"{origin}_{destination}_{date.strftime("%Y-%m-%d")}_{transportation_mode}_{payment_type}"

        # Add flight details to cache
        cache_manager.set_cache(cache_key,
                                {"origin": origin, "destination": destination, "date": date.strftime("%Y-%m-%d"),
                                    "price": flight_details["price"], "duration": flight_details["duration"],
                                    "airline": flight_details["airline"]})

        print("Flight details successfully added to the cache.")


if __name__ == "__main__":
    main()
