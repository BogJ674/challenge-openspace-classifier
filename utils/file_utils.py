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

    @staticmethod
    def load_seating(filename: str) -> list[tuple]:
        """Load seating arrangement from a CSV file.

        :param filename: path to the CSV file containing seating arrangement.
        :return: list of tuples containing (table_number, seat_number, occupant)."""
        data = []
        try:
            with open(filename, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                for row in reader:
                    if row and len(row) >= 3:
                        table_num = int(row[0])
                        seat_num = int(row[1])
                        occupant = row[2]
                        data.append((table_num, seat_num, occupant))
        except FileNotFoundError:
            return []
        return data

    @staticmethod
    def store_openspace_state(filename: str, state: dict) -> None:
        """Store complete openspace state to a JSON file.

        :param filename: path to the output JSON file.
        :param state: dictionary containing complete openspace state.
        :return: None"""
        with open(filename, mode="w", encoding="utf-8") as file:
            json.dump(state, file, indent=2, ensure_ascii=False)

    @staticmethod
    def load_openspace_state(filename: str) -> dict:
        """Load complete openspace state from a JSON file.

        :param filename: path to the JSON file containing openspace state.
        :return: dictionary containing openspace state, or empty dict if file not found."""
        try:
            with open(filename, mode="r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    @staticmethod
    def add_colleague_to_file(filename: str, colleague_name: str) -> bool:
        """Add a new colleague to the colleagues CSV file.

        :param filename: path to the colleagues CSV file.
        :param colleague_name: name of the colleague to add.
        :return: True if added successfully, False if already exists."""
        try:
            # Load existing colleagues
            existing_colleagues = FileUtils.load_colleagues(filename)

            # Check if colleague already exists
            if colleague_name in existing_colleagues:
                return False

            # Add new colleague
            existing_colleagues.append(colleague_name)

            # Write back to file
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                for name in existing_colleagues:
                    writer.writerow([name])

            return True
        except FileNotFoundError:
            # Create new file with this colleague
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([colleague_name])
            return True
