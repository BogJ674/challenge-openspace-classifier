from utils.table import Table, Seat
from utils.file_utils import FileUtils
import random


class Openspace:
    """Class to represent an openspace with multiple tables.

    :attr tables (list[Table]): which is a list of table objects.
    :attr number_of_tables (int): representing the number of tables in the openspace."""

    def __init__(self, number_of_tables: int, table_capacity: int, input_file: str = "new_colleagues.csv") -> None:
        self.number_of_tables: int = number_of_tables
        self.table_capacity: int = table_capacity
        self.input_file: str = input_file
        self.tables: list[Table] = [
            Table(table_capacity) for _ in range(number_of_tables)
        ]
        self.unseated: list[str] = []
        self.preferences: dict = {"whitelist": {}, "blacklist": {}}
    
    def clear_all_tables(self) -> None:
        """Clear all tables and unseat everyone.

        :return: None"""
        for table in self.tables:
            table.seats = [Seat() for i in range(self.table_capacity)]
        self.unseated = []

    def calculate_table_distribution(self, num_people: int) -> list[int]:
        """
        Calculates the optimal distribution of people across tables.
        Aims to fill tables as evenly as possible, avoiding single-person tables.

        Rules:
        - Fill tables completely when possible
        - Distribute remainder evenly across tables
        - Avoid leaving anyone alone at a table
        - Leave entire tables empty rather than having single occupants

        :param num_people: number of people to seat.
        :return: list of integers representing how many people at each table.

        Examples:
        - 6 tables of 4, 22 people -> [4, 4, 4, 4, 3, 3] (4 full, 2 with 3)
        - 7 tables of 4, 24 people -> [4, 4, 4, 4, 4, 4, 0] (6 full, 1 empty)
        - 7 tables of 4, 25 people -> [4, 4, 4, 4, 3, 3, 3] (4 full, 3 with 3)
        - 4 tables of 4, 7 people -> [4, 3, 0, 0] (1 full, 1 with 3, 2 empty)
        """
        total_capacity = self.number_of_tables * self.table_capacity

        # If more people than capacity, we'll seat as many as possible
        people_to_seat = min(num_people, total_capacity)

        # Handle edge case: no people to seat
        if people_to_seat == 0:
            return [0] * self.number_of_tables

        # Calculate how many tables we need
        tables_needed = (people_to_seat + self.table_capacity - 1) // self.table_capacity

        # Calculate base distribution
        people_per_table = people_to_seat // tables_needed
        remainder = people_to_seat % tables_needed

        # Special case: if we would create a single-person table, adjust
        if people_per_table == 0 and remainder == 1 and tables_needed == 1:
            # Can't avoid single person - this is the case of 1 person total
            return [1] + [0] * (self.number_of_tables - 1)

        # If people_per_table is 1 and we have remainder, we'd create single-person tables
        # Instead, try to use fewer tables with more people each
        if people_per_table == 1 and remainder > 0 and tables_needed > 1:
            # Recalculate to minimize single-person tables
            # Try to fit people in fewer tables
            tables_needed = max(1, (people_to_seat + 1) // 2)  # At least 2 per table
            people_per_table = people_to_seat // tables_needed
            remainder = people_to_seat % tables_needed

        # Build distribution list
        distribution = []

        # Tables with extra person (base + 1)
        for _ in range(remainder):
            distribution.append(people_per_table + 1)

        # Tables with base amount
        for _ in range(tables_needed - remainder):
            distribution.append(people_per_table)

        # Empty tables
        for _ in range(self.number_of_tables - tables_needed):
            distribution.append(0)

        return distribution

    def _can_sit_at_table(self, person: str, table_idx: int) -> bool:
        """Check if a person can sit at a table based on blacklist preferences.

        :param person: name of the person to check
        :param table_idx: index of the table to check
        :return: True if person can sit at table, False if blacklist violation"""

        table = self.tables[table_idx]

        # Check if person has blacklist preferences and anyone they avoid is at this table
        if person in self.preferences["blacklist"]:
            avoided_people = self.preferences["blacklist"][person]
            for seat in table.seats:
                if not seat.free and seat.occupant in avoided_people:
                    return False

        # Also check reverse - if anyone at the table has this person on their blacklist
        for seat in table.seats:
            if not seat.free:
                occupant = seat.occupant
                if occupant in self.preferences["blacklist"]:
                    if person in self.preferences["blacklist"][occupant]:
                        return False

        return True

    def _has_blacklist_conflict(self, person1: str, person2: str) -> bool:
        """Check if two people have a blacklist conflict.

        :param person1: first person's name
        :param person2: second person's name
        :return: True if they should not sit together, False otherwise"""

        # Check if person1 has person2 on their blacklist
        if person1 in self.preferences["blacklist"]:
            if person2 in self.preferences["blacklist"][person1]:
                return True

        # Check if person2 has person1 on their blacklist
        if person2 in self.preferences["blacklist"]:
            if person1 in self.preferences["blacklist"][person2]:
                return True

        return False

    def _get_whitelist_groups(self, names: list[str]) -> list[set]:
        """Create groups of people who want to sit together based on whitelist.
        Groups are split if there are blacklist conflicts between members.

        :param names: list of all names to organize
        :return: list of sets, where each set is a group of people who want to sit together"""

        # Build a graph of whitelist connections
        graph = {}
        for person in names:
            graph[person] = set()

        # Add all whitelist connections (even one-way), but only if no blacklist conflict
        for person, targets in self.preferences["whitelist"].items():
            if person in graph:
                for target in targets:
                    if target in graph:
                        # Check for blacklist conflict before adding connection
                        if not self._has_blacklist_conflict(person, target):
                            graph[person].add(target)
                            # Make it bidirectional - if A wants B, seat them together
                            graph[target].add(person)

        # Find connected components (groups) using DFS
        groups = []
        processed = set()

        def has_group_conflict(person, group):
            """Check if person has blacklist conflict with anyone in the group."""
            for member in group:
                if self._has_blacklist_conflict(person, member):
                    return True
            return False

        def dfs(node, group):
            """Depth-first search to find all connected people without blacklist conflicts."""
            if node in processed:
                return

            # Check if this node conflicts with anyone already in the group
            if has_group_conflict(node, group):
                return

            processed.add(node)
            group.add(node)
            for neighbor in graph[node]:
                if neighbor not in processed:
                    dfs(neighbor, group)

        for person in names:
            if person not in processed:
                group = set()
                dfs(person, group)
                if len(group) > 1:
                    groups.append(group)

        return groups

    def organize(self, names: list[str]) -> dict:
        """
        Assigns people to Seat objects respecting whitelist and blacklist preferences.
        Uses calculate_table_distribution to ensure optimal seating arrangement.
        If there are too many people, they are added to the unseated list.

        :param names: list of names to be assigned to seats.
        :return: dict with preference satisfaction statistics"""

        self.clear_all_tables()
        self.unseated = []  # Reset unseated list

        remaining_names = names.copy()
        seated_names = []

        # Phase 1: Handle whitelist groups - seat people who want to sit together
        whitelist_groups = self._get_whitelist_groups(remaining_names)

        # Sort groups by size (largest first) to maximize satisfaction
        whitelist_groups.sort(key=len, reverse=True)

        for group in whitelist_groups:
            group_list = list(group)

            # Try to find a table that can accommodate this group
            for table_idx, table in enumerate(self.tables):
                if table.left_capacity() >= len(group_list):
                    # Check if all group members can sit at this table (no blacklist violations)
                    can_all_sit = True
                    for person in group_list:
                        if not self._can_sit_at_table(person, table_idx):
                            can_all_sit = False
                            break

                    if can_all_sit:
                        # Seat the entire group at this table
                        for person in group_list:
                            table.assign_seat(person)
                            seated_names.append(person)
                            remaining_names.remove(person)
                        break

        # Phase 2: Seat remaining people while respecting blacklist and using optimal distribution
        random.shuffle(remaining_names)

        # Get current occupancy of each table
        current_occupancy = [self.table_capacity - table.left_capacity() for table in self.tables]

        # Calculate target distribution for remaining people
        # We need to consider what's already seated
        total_to_seat = len(remaining_names)
        total_already_seated = sum(current_occupancy)
        total_people = total_already_seated + total_to_seat

        # Calculate the ideal final distribution
        ideal_distribution = self.calculate_table_distribution(total_people)

        # Calculate how many MORE people each table needs to reach ideal distribution
        target_additions = []
        for table_idx in range(self.number_of_tables):
            current = current_occupancy[table_idx]
            ideal = ideal_distribution[table_idx]
            needed = max(0, ideal - current)  # How many more people this table needs
            target_additions.append(needed)

        # Create table priority list: (table_idx, spots_needed), sorted by spots needed (descending)
        table_priority = [(idx, needed) for idx, needed in enumerate(target_additions) if needed > 0]
        table_priority.sort(key=lambda x: x[1], reverse=True)

        # Track which people we've tried to seat
        remaining_people = remaining_names.copy()

        # Try to fill tables according to priority
        for table_idx, spots_needed in table_priority:
            spots_filled = 0
            people_to_remove = []

            for person in remaining_people:
                if spots_filled >= spots_needed:
                    break

                # Check if this person can sit at this table
                if self.tables[table_idx].has_free_spot() and self._can_sit_at_table(person, table_idx):
                    self.tables[table_idx].assign_seat(person)
                    seated_names.append(person)
                    people_to_remove.append(person)
                    spots_filled += 1

            # Remove seated people from remaining list
            for person in people_to_remove:
                remaining_people.remove(person)

        # Phase 2b: Handle any remaining people who couldn't be seated due to distribution or blacklist
        # Try to seat them at any available table
        for person in remaining_people:
            seated = False

            # Try to find any suitable table
            for table_idx, table in enumerate(self.tables):
                if table.has_free_spot() and self._can_sit_at_table(person, table_idx):
                    table.assign_seat(person)
                    seated_names.append(person)
                    seated = True
                    break

            # If couldn't seat due to blacklist or capacity, add to unseated
            if not seated:
                self.unseated.append(person)

        # Phase 3: Calculate and return preference statistics
        stats = self._calculate_preference_stats()

        # Print violations
        if stats["whitelist_violated"] > 0 or stats["blacklist_violated"] > 0:
            print(f"\n{'-' * 50}")
            print("PREFERENCE VIOLATIONS:")
            print(f"{'-' * 50}")

            if stats["whitelist_violated"] > 0:
                print(f"\nWhitelist violations ({stats['whitelist_violated']}):")
                for person, preferred_people in self.preferences["whitelist"].items():
                    person_table = self._find_person_table(person)
                    if person_table is None:
                        continue
                    for preferred in preferred_people:
                        preferred_table = self._find_person_table(preferred)
                        if preferred_table != person_table:
                            print(f"  - {person} wants to sit with {preferred} (not at same table)")

            if stats["blacklist_violated"] > 0:
                print(f"\nBlacklist violations ({stats['blacklist_violated']}):")
                for person, avoided_people in self.preferences["blacklist"].items():
                    person_table = self._find_person_table(person)
                    if person_table is None:
                        continue
                    for avoided in avoided_people:
                        avoided_table = self._find_person_table(avoided)
                        if avoided_table == person_table:
                            print(f"  - {person} wants to avoid {avoided} (seated together at table {person_table + 1})")

            print(f"{'-' * 50}\n")

        return stats

    def _find_person_table(self, person_name: str) -> int | None:
        """Find which table a person is seated at.

        :param person_name: name of person to find
        :return: table index or None if not seated"""
        for idx, table in enumerate(self.tables):
            for seat in table.seats:
                if not seat.free and seat.occupant == person_name:
                    return idx
        return None

    def _calculate_preference_stats(self) -> dict:
        """Calculate how many preferences are satisfied vs violated.

        :return: dict with satisfaction statistics"""
        stats = {
            'whitelist_satisfied': 0,
            'whitelist_violated': 0,
            'blacklist_satisfied': 0,
            'blacklist_violated': 0
        }

        # Check whitelist
        for person, preferred_people in self.preferences["whitelist"].items():
            person_table = self._find_person_table(person)
            if person_table is None:
                continue

            for preferred in preferred_people:
                preferred_table = self._find_person_table(preferred)
                if preferred_table == person_table:
                    stats['whitelist_satisfied'] += 1
                else:
                    stats['whitelist_violated'] += 1

        # Check blacklist
        for person, avoided_people in self.preferences["blacklist"].items():
            person_table = self._find_person_table(person)
            if person_table is None:
                continue

            for avoided in avoided_people:
                avoided_table = self._find_person_table(avoided)
                if avoided_table != person_table or avoided_table is None:
                    stats['blacklist_satisfied'] += 1
                else:
                    stats['blacklist_violated'] += 1

        return stats

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
        # Check if filename is JSON or CSV
        if filename.endswith('.json'):
            # Store complete state in JSON format
            self.store_complete_state(filename)
        else:
            # Legacy CSV format - only seating arrangement
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

    def store_complete_state(self, filename: str = "openspace_state.json") -> None:
        """Store complete openspace state including preferences and configuration.

        :param filename: name of the JSON file to store the state.
        :return: None"""
        # Build complete state dictionary
        state = {
            "config": {
                "number_of_tables": self.number_of_tables,
                "table_capacity": self.table_capacity,
                "input_file": self.input_file
            },
            "tables": [],
            "unseated": self.unseated.copy(),
            "preferences": self.preferences.copy()
        }

        # Add table data
        for i, table in enumerate(self.tables):
            table_data = {
                "table_number": i + 1,
                "seats": []
            }
            for j, seat in enumerate(table.seats):
                seat_data = {
                    "seat_number": j + 1,
                    "occupant": seat.occupant if not seat.free else None,
                    "free": seat.free
                }
                table_data["seats"].append(seat_data)
            state["tables"].append(table_data)

        # Use FileUtils to store the complete state
        FileUtils.store_openspace_state(filename, state)

    def load_from_file(self, filename: str) -> bool:
        """Load seating arrangement from a file (CSV or JSON).

        :param filename: name of the file to load from.
        :return: True if loaded successfully, False otherwise."""

        # Check if it's a JSON file
        if filename.endswith('.json'):
            return self.load_complete_state(filename)
        else:
            # Legacy CSV format
            data = FileUtils.load_seating(filename)
            if not data:
                return False

            # Clear current seating
            self.unseated = []

            # Find max table number in the file
            max_table = max([row[0] for row in data if row[0] > 0], default=0)

            # If file has more tables than current config, move extra people to unseated
            if max_table > self.number_of_tables:
                print(f"Warning: File has {max_table} tables but room only has {self.number_of_tables} tables.")

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
                        # Only seat if within current table/capacity limits
                        if table_idx < self.number_of_tables and seat_idx < self.table_capacity:
                            self.tables[table_idx].seats[seat_idx].set_occupant(occupant)
                        else:
                            # Person was at a table that no longer exists
                            self.unseated.append(occupant)

            return True

    def load_complete_state(self, filename: str = "openspace_state.json") -> bool:
        """Load complete openspace state from a JSON file.

        :param filename: name of the JSON file to load from.
        :return: True if loaded successfully, False otherwise."""
        state = FileUtils.load_openspace_state(filename)
        if not state:
            return False

        # Load config if present
        if "config" in state:
            config = state["config"]
            self.number_of_tables = config.get("number_of_tables", self.number_of_tables)
            self.table_capacity = config.get("table_capacity", self.table_capacity)
            self.input_file = config.get("input_file", self.input_file)

            # Recreate tables with new configuration
            self.tables = [Table(self.table_capacity) for _ in range(self.number_of_tables)]

        # Clear current seating
        self.unseated = []

        # Clear all tables
        for table in self.tables:
            table.seats = [Seat() for _ in range(self.table_capacity)]

        # Load preferences
        if "preferences" in state:
            self.preferences = state["preferences"]

        # Load unseated people
        if "unseated" in state:
            self.unseated = state["unseated"]

        # Load table data
        if "tables" in state:
            for table_data in state["tables"]:
                table_idx = table_data["table_number"] - 1

                # Only load tables that fit in current configuration
                if table_idx >= self.number_of_tables:
                    # Move people from extra tables to unseated
                    for seat_data in table_data["seats"]:
                        if seat_data["occupant"] is not None:
                            self.unseated.append(seat_data["occupant"])
                    continue

                # Load seats
                for seat_data in table_data["seats"]:
                    seat_idx = seat_data["seat_number"] - 1

                    # Only load seats that fit in current capacity
                    if seat_idx >= self.table_capacity:
                        if seat_data["occupant"] is not None:
                            self.unseated.append(seat_data["occupant"])
                        continue

                    if seat_data["occupant"] is not None:
                        self.tables[table_idx].seats[seat_idx].set_occupant(seat_data["occupant"])

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
