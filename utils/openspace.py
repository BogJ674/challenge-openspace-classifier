from utils.table import Table, Seat
from utils.file_utils import FileUtils


class Openspace:
    """Class to represent an openspace with multiple tables.

    :attr tables (list[Table]): which is a list of table objects.
    :attr number_of_tables (int): representing the number of tables in the openspace."""

    def __init__(self, number_of_tables: int, table_capacity: int) -> None:
        self.number_of_tables: int = number_of_tables
        self.table_capacity: int = table_capacity
        self.tables: list[Table] = [
            Table(table_capacity) for _ in range(number_of_tables)
        ]
        self.unseated: list[str] = []

    def organize(self, names: list[str]) -> None:
        """
        Randomly assigns people to Seat objects in the different Table objects.
        If there are too many people, they are added to the unseated list.

        :param names: list of names to be assigned to seats.
        :return: None"""
        import random

        random.shuffle(names)
        self.unseated = []  # Reset unseated list
        name_index = 0

        for table in self.tables:
            while table.has_free_spot() and name_index < len(names):
                table.assign_seat(names[name_index])
                name_index += 1

        # Add remaining people to unseated list
        while name_index < len(names):
            self.unseated.append(names[name_index])
            name_index += 1

    def get_remaining_seats(self) -> int:
        """Returns the number of remaining free seats in the openspace.

        :return: Number of free seats"""
        remaining = 0
        for table in self.tables:
            remaining += table.left_capacity()
        return remaining
    
    def get_seated_count(self) -> int:
        """Returns the number of seats filled in.

        :return: Number of seated colleagues"""
        seated = 0
        for table in self.tables:
            seated += table.capacity - table.left_capacity()
        return seated

    def display(self) -> None:
        """Displays the different tables and their occupants in a nice and readable way.

        :return: None"""
        for i, table in enumerate(self.tables):
            print(f"Table {i+1}:")
            print(table)
            print("-" * 20)

    def display_statistics(self) -> None:
        """Displays statistics about the seating arrangement.

        :return: None"""
        remaining_seats = self.get_remaining_seats()
        total_capacity = self.number_of_tables * self.table_capacity
        seated_count = self.get_seated_count()

        print("\n" + "=" * 40)
        print("STATISTICS")
        print("=" * 40)
        print(f"Total capacity: {total_capacity} seats")
        print(f"People seated: {seated_count}")
        print(f"Remaining seats: {remaining_seats}")

        # Display unseated people if any
        if self.unseated:
            print(f"\nWARNING: {len(self.unseated)} people could not be seated!")
            print("Unseated colleagues:")
            for name in self.unseated:
                print(f"  - {name}")

    def store(self, filename: str = "output.csv") -> None:
        """Stores the repartition in a file. default: output.csv

        :param filename: name of the file to store the repartition. (default: output.csv)
        :return: None"""
        # Prepare data as list of tuples
        data = []
        for i, table in enumerate(self.tables):
            for j, seat in enumerate(table.seats):
                data.append(
                    (i + 1, j + 1, seat.occupant if not seat.free else "Free")
                )

        # Add unseated colleagues with table 0 and seat 0
        for name in self.unseated:
            data.append((0, 0, name))

        # Use FileUtils to store the data
        FileUtils.store_seating(filename, data)
