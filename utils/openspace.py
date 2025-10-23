from utils.table import Table, Seat
from utils.file_utils import FileUtils
import random


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
        self.preferences: dict = {"whitelist": {}, "blacklist": {}}

    def organize(self, names: list[str]) -> None:
        """
        Randomly assigns people to Seat objects in the different Table objects.
        If there are too many people, they are added to the unseated list.

        :param names: list of names to be assigned to seats.
        :return: None"""

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

    def load_from_file(self, filename: str) -> bool:
        """Load seating arrangement from a CSV file.

        :param filename: name of the file to load from.
        :return: True if loaded successfully, False otherwise."""
        data = FileUtils.load_seating(filename)
        if not data:
            return False

        # Clear current seating
        self.unseated = []

        # Find max table number to adjust number of tables if needed
        max_table = max([row[0] for row in data if row[0] > 0], default=0)
        if max_table > self.number_of_tables:
            # Add more tables if needed
            for _ in range(max_table - self.number_of_tables):
                self.tables.append(Table(self.table_capacity))
            self.number_of_tables = max_table

        # Clear all tables
        for table in self.tables:
            table.seats = [Seat() for _ in range(self.table_capacity)]

        # Assign people from the file
        for table_num, seat_num, occupant in data:
            if occupant != "Free":
                if table_num == 0:
                    # Unseated person
                    self.unseated.append(occupant)
                else:
                    # Seated person
                    table_idx = table_num - 1
                    seat_idx = seat_num - 1
                    if table_idx < len(self.tables) and seat_idx < self.table_capacity:
                        self.tables[table_idx].seats[seat_idx].set_occupant(occupant)

        return True

    def get_people_alone_count(self) -> int:
        """Count the number of people sitting alone at tables.

        :return: Number of people alone at tables."""
        alone_count = 0
        for table in self.tables:
            occupied_seats = sum(1 for seat in table.seats if not seat.free)
            if occupied_seats == 1:
                alone_count += 1
        return alone_count

    def add_colleague(self, name: str) -> bool:
        """Add a new colleague to the room. Tries to find a free seat.

        :param name: name of the colleague to add.
        :return: True if seated successfully, False if no seats available."""
        for table in self.tables:
            if table.has_free_spot():
                table.assign_seat(name)
                return True

        # No free spot found
        self.unseated.append(name)
        return False

    def add_table(self) -> None:
        """Add a new table to the openspace.

        :return: None"""
        self.tables.append(Table(self.table_capacity))
        self.number_of_tables += 1

    def set_preference(self, person: str, preference_type: str, target: str) -> None:
        """Set a seating preference (whitelist or blacklist).

        :param person: the person who has the preference.
        :param preference_type: either 'whitelist' or 'blacklist'.
        :param target: the person they want to sit with (whitelist) or avoid (blacklist).
        :return: None"""
        if preference_type not in ["whitelist", "blacklist"]:
            return

        if person not in self.preferences[preference_type]:
            self.preferences[preference_type][person] = []

        if target not in self.preferences[preference_type][person]:
            self.preferences[preference_type][person].append(target)

    def get_total_seats(self) -> int:
        """Get the total number of seats in the room.

        :return: Total number of seats."""
        return self.number_of_tables * self.table_capacity
