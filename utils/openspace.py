from utils.table import Table, Seat


class Openspace:
    """Class to represent an openspace with multiple tables.

    :attr tables (list[Table]): which is a list of table objects.
    :attr number_of_tables (int): representing the number of tables in the openspace."""

    def __init__(self, number_of_tables: int, table_capacity: int) -> None:
        self.number_of_tables: int = number_of_tables
        self.tables: list[Table] = [
            Table(table_capacity) for _ in range(number_of_tables)
        ]

    def organize(self, names: list[str]) -> None:
        """
        Randomly assigns people to Seat objects in the different Table objects.

        :param names: list of names to be assigned to seats.
        :return: None"""
        import random

        random.shuffle(names)
        name_index = 0
        for table in self.tables:
            while table.has_free_spot() and name_index < len(names):
                table.assign_seat(names[name_index])
                name_index += 1

    def display(self) -> None:
        """Displays the different tables and their occupants in a nice and readable way.

        :return: None"""
        for i, table in enumerate(self.tables):
            print(f"Table {i+1}:")
            print(table)
            print("-" * 20)

    def store(self, filename: str = "output.csv") -> None:
        """Stores the repartition in a file. default: output.csv

        :param filename: name of the file to store the repartition. (default: output.csv)
        :return: None"""
        import csv

        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Table Number", "Seat Number", "Occupant"])
            for i, table in enumerate(self.tables):
                for j, seat in enumerate(table.seats):
                    writer.writerow(
                        [i + 1, j + 1, seat.occupant if not seat.free else "Free"]
                    )
