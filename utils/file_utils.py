import csv
import json


class FileUtils:
    """Utility class for loading and storing CSV files."""

    @staticmethod
    def load_config(filename: str = "config.json") -> dict:
        """Load configuration from a JSON file.

        :param filename: path to the JSON configuration file (default: config.json).
        :return: dictionary containing configuration values."""
        with open(filename, mode="r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def load_colleagues(filename: str) -> list[str]:
        """Load colleague names from a CSV file.
|
        :param filename: path to the CSV file containing colleague names.
        :return: list of colleague names."""
        names = []
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Skip empty rows
                    names.append(row[0].strip())
        return names

    @staticmethod
    def store_seating(filename: str, data: list[tuple]) -> None:
        """Store seating arrangement to a CSV file.

        :param filename: path to the output CSV file.
        :param data: list of tuples containing (table_number, seat_number, occupant).
        :return: None"""
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Table Number", "Seat Number", "Occupant"])
            writer.writerows(data)
