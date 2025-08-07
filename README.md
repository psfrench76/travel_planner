# Travel Search

## Introduction

This project is a Python-based travel search and flight management system designed to help users plan and optimize their
travel itineraries. It provides functionality for managing flight data, searching for the least-cost travel paths, and
applying constraints such as visit durations or disallowed dates for specific destinations. The system uses a modular
architecture with components for caching, user input handling, and external data connectors.

Key features include:

- **Flight Data Management**: Add and manage flight details manually or via connectors (not yet implemented -- this data
  is hard to acquire).
- **Travel Search**: Perform A* search to find the least-cost round-trip path while visiting specified destinations.
- **Custom Constraints**: Support for user-defined constraints, such as the number of days to spend at each destination.

## Usage

### Adding Flights (`add_flights.py`)

The `add_flights.py` script allows users to manually input flight details into the system. This is useful for scenarios
where automated data fetching is unavailable or unnecessary.

#### Example Usage:

1. Run the script:
   ```bash
   python add_flights.py
2. Follow the prompts to enter flight details such as origin, destination, date, price, and other details.
3. Use **calendar mode** to quickly input prices for a range of dates without re-entering the origin and destination for
   each entry. In this mode:
    * After entering the origin and destination, you can input prices for multiple dates sequentially.
    * Type `done` to exit calendar mode when finished.
4. The data will be stored in the system for later use in travel searches.

### Travel Search (`travel_search.py`)

The `travel_search.py` script is the main interface for planning and optimizing travel itineraries. It uses an A* search
algorithm to find the least-cost round-trip path while visiting all specified destinations.

#### Example Usage:

1. Run the script:
   ```bash
   python travel_search.py
   ```
2. Provide the required inputs:
    * Origin: The starting point of your journey.
    * Destinations: A list of destinations to visit, along with the range of days to spend at each location.
    * The system will calculate the optimal path and display the results.

Sample input format:

```
Enter the origin: JFK
Enter destinations to visit and the range of days to spend there (type 'done' to finish):
Enter destination: LAX
Enter the minimum number of days to spend in LAX: 2
Enter the maximum number of days to spend in LAX: 5
Enter destination: SFO
Enter the minimum number of days to spend in SFO: 3
Enter the maximum number of days to spend in SFO: 4
Enter destination: done
```

Sample output:

```
Round-trip path:
JFK -> LAX (Date: 2023-12-01, Cost: 300)
LAX -> SFO (Date: 2023-12-04, Cost: 200)
SFO -> JFK (Date: 2023-12-07, Cost: 400)
Total cost: 900
```