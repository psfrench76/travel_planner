# Python
import heapq
from datetime import datetime
from typing import Dict, List, Tuple
import json
import os


# Python
class FlightGraph:

    def __init__(self, cache_dir: str):
        self.graph = {}  # Dictionary to store nodes and edges
        self.cache_dir = cache_dir

    def add_leg(self, origin: str, destination: str, date: str, price: float, duration: str, airline: str):
        """Adds a journey leg to the graph."""
        if origin not in self.graph:
            self.graph[origin] = []
        self.graph[origin].append(
            {"destination": destination, "date": date, "price": price, "duration": duration, "airline": airline})

    def get_legs(self, origin: str) -> List[Dict]:
        """Returns all journey legs from a given origin."""
        return self.graph.get(origin, [])

    def heuristic(self, origin, current: str, destinations: List[str]) -> float:
        """Heuristic function estimating the cost to visit remaining destinations."""
        remaining_destinations = set(destinations)
        legs = self.graph.get(current, [])
        prices = [leg["price"] for leg in legs if leg["destination"] in remaining_destinations]
        if prices:
            return min(prices)  # Return the minimum price to any remaining destination
        else:
            if current != origin:
                legs = self.graph.get(current, [])
                prices = [leg["price"] for leg in legs if leg["destination"] == origin]
                if prices:
                    return min(prices)
            else:
                return 0

        return float("inf")  # If no legs available, return infinity

    # TODO: possible for date constraints to be fully within visit, this will not catch that
    # Python
    def find_least_cost_path(self, origin: str, destinations: Dict[str, Tuple[int, int]],
                             constraints: Dict[str, List[Tuple[str, str]]]) -> Tuple[
        List[Tuple[str, str, float]], float]:
        """
        Finds the least-cost path visiting all destinations using A* search.
        :param origin: Starting point of the journey.
        :param destinations: Dictionary of destinations with visit length constraints (e.g., {"NYC": (2, 5)}).
        :return: Tuple containing the best path and its cost.
        """
        print("Starting A* search...")
        pq = [(0, 0, origin, [], None,
               destinations)]  # (priority, current_node, path, current_date, remaining_destinations)
        best_path = None
        best_cost = float("inf")

        while pq:
            priority, cost, current, path, current_date, remaining_destinations = heapq.heappop(pq)

            if cost >= best_cost:
                # print(f"Skipping node {current} due to cost: {cost} >= best cost: {best_cost}")
                continue

            # print(f"Exploring node: {current}, Cost: {cost}, Remaining destinations: {remaining_destinations}")

            if not remaining_destinations and current == origin:
                print(f"Completed path: {path}, Total cost: {cost}")
                if cost < best_cost:
                    best_path = path
                    best_cost = cost
                continue

            for leg in self.graph.get(current, []):
                leg_date = datetime.strptime(leg["date"], "%Y-%m-%d")
                if current_date:
                    previous_date = datetime.strptime(current_date, "%Y-%m-%d")
                    visit_length = (leg_date - previous_date).days

                    # Check if visit length matches the constraint
                    if current in destinations:
                        min_days, max_days = destinations[current]
                        if not (min_days <= visit_length <= max_days):
                            # print(f"Skipping leg due to invalid visit length: {visit_length} days")
                            continue

                # print(f"Checking leg from: {current} to: {leg['destination']}, Date: {leg['date']}")
                if current in constraints:
                    if self.date_violates_constraints(leg_date, constraints[current]):
                        continue
                if leg["destination"] in constraints:
                    if self.date_violates_constraints(leg_date, constraints[leg["destination"]]):
                        continue

                next_cost = cost + leg["price"]  # Actual cost of the path
                heuristic_cost = self.heuristic(origin, leg["destination"], list(remaining_destinations.keys()))
                next_path = path + [(leg["destination"], leg["date"], leg["price"])]
                next_remaining = {dest: days for dest, days in remaining_destinations.items() if
                                  dest != leg["destination"]}

                if next_cost + heuristic_cost >= best_cost:
                    # print(f"Skipping leg due to cost: {next_cost + heuristic_cost} >= {best_cost}")
                    continue

                # print(f"Pushing to queue: Destination: {leg['destination']}, Cost: {next_cost}, Heuristic: {
                # heuristic_cost}")
                heapq.heappush(pq, (next_cost + heuristic_cost, next_cost, leg["destination"], next_path, leg["date"],
                                    next_remaining))

        if best_path is None:
            print("No valid path found.")
        return best_path, best_cost

    def date_violates_constraints(self, date: datetime, constraints: List[Tuple[str, str]]) -> bool:
        """
        Checks if a given date is within any of the date constraints.
        :param date: Date to check in YYYY-MM-DD format.
        :param constraints: Dictionary of constraints with destination as key and list of (start_date, end_date) tuples.
        :return: True if the date is within any constraint, False otherwise.
        """

        for start_date, end_date in constraints:
            if datetime.strptime(start_date, "%Y-%m-%d") <= date <= datetime.strptime(end_date, "%Y-%m-%d"):
                # print(f"Skipping leg due to date constraint: {date.strftime("%Y-%m-%d")} in {start_date} to {
                # end_date}")
                return True
        return False
