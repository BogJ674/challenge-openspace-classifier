from utils.openspace import Openspace
from utils.table import Table
from utils.file_utils import FileUtils
import sys
import os


# ANSI color codes
class Colors:
    """
    ANSI color codes for terminal output formatting.

    This class provides constants for various text colors and background colors
    to be used in terminal output.
    """
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Regular colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Background colors
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"


def clear_terminal() -> None:
    """
    Clear the terminal screen.

    Uses the appropriate system command for clearing the terminal based on the operating system.
    """
    os.system("cls" if os.name == "nt" else "clear")


def display_statistics_footer(openspace: Openspace) -> None:
    """
    Display statistics footer at the bottom of the screen.

    :param openspace: The Openspace instance containing the seating arrangement.
    """
    people_seated = openspace.get_seated_count()
    available_seats = openspace.get_remaining_seats()
    people_alone = openspace.get_people_alone_count()

    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}STATS:{Colors.RESET} ", end="")
    print(f"{Colors.GREEN}Seated: {people_seated}{Colors.RESET} | ", end="")
    print(f"{Colors.YELLOW}Available: {available_seats}{Colors.RESET} | ", end="")
    print(f"{Colors.MAGENTA}Alone: {people_alone}{Colors.RESET}", end="")
    if openspace.unseated:
        print(
            f"\n| {Colors.RED}Unseated!: {len(openspace.unseated)}{Colors.RESET}", end=""
        )
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")


def display_menu(openspace: Openspace) -> None:
    """
    Display the main menu.

    :param openspace: The Openspace instance containing the seating arrangement.
    """
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}OPENSPACE SEATING ORGANIZER{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    print(f"\n{Colors.YELLOW}{Colors.BOLD}=== SETUP & CONFIGURATION ==={Colors.RESET}")
    print(
        f"{Colors.GREEN}1.{Colors.RESET} Configure room (tables, capacity, load/save config)"
    )
    print(f"{Colors.GREEN}2.{Colors.RESET} Organize initial seating arrangement")
    print(f"\n{Colors.YELLOW}{Colors.BOLD}=== DYNAMIC CHANGES ==={Colors.RESET}")
    print(f"{Colors.GREEN}3.{Colors.RESET} Add a colleague (late arrival)")
    print(f"{Colors.GREEN}4.{Colors.RESET} Add a table")
    print(f"{Colors.GREEN}5.{Colors.RESET} Re-organize seating")
    print(f"\n{Colors.YELLOW}{Colors.BOLD}=== PREFERENCES ==={Colors.RESET}")
    print(
        f"{Colors.GREEN}6.{Colors.RESET} Manage seating preferences (white/blacklist)"
    )
    print(f"\n{Colors.YELLOW}{Colors.BOLD}=== VIEW INFO ==={Colors.RESET}")
    print(f"{Colors.GREEN}7.{Colors.RESET} See current arrangement")
    print(f"{Colors.GREEN}8.{Colors.RESET} See room statistics")
    print(f"\n{Colors.RED}9.{Colors.RESET} Exit")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")

    display_statistics_footer(openspace)


def configure_room(openspace: Openspace) -> bool:
    """
    Configure room setup.

    :param openspace: The Openspace instance to configure.
    :return: A bool indicating if room dimensions changed (True) or not (False).
    """
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== ROOM CONFIGURATION ==={Colors.RESET}\n")
    print(f"{Colors.GREEN}1.{Colors.RESET} Change room dimensions")
    print(f"{Colors.GREEN}2.{Colors.RESET} Change input file")
    print(f"{Colors.GREEN}3.{Colors.RESET} Back to main menu")

    choice = input("\nEnter your choice (1-3): ")

    if choice == "1":
        try:
            old_tables = openspace.number_of_tables
            old_capacity = openspace.table_capacity

            print(f"\nCurrent: {old_tables} tables of capacity {old_capacity}")
            tables = int(input("Enter number of tables: "))
            capacity = int(input("Enter table capacity: "))

            openspace.number_of_tables = tables
            openspace.table_capacity = capacity

            print(f"\n{Colors.GREEN}Configuration updated successfully!{Colors.RESET}")
            input("Press Enter to continue...")
            config_changed = (old_tables != tables or old_capacity != capacity)
            return config_changed
        except ValueError:
            print(
                f"\n{Colors.RED}Invalid input! Configuration not changed.{Colors.RESET}"
            )
            input("Press Enter to continue...")
            return False
    elif choice == "2":
        print(f"\nCurrent input file: {openspace.input_file}")
        input_file = input("Enter new input file path: ").strip()
        if input_file:
            openspace.input_file = input_file
            print(f"\n{Colors.GREEN}Input file updated to: {input_file}{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}Input file not changed.{Colors.RESET}")
        input("Press Enter to continue...")
        return False
    else:
        return False


def organize_seating(openspace: Openspace, state_file: str) -> None:
    """
    Organize initial seating arrangement.

    :param openspace: The Openspace instance to organize.
    :param state_file: A str path to the state file for saving the arrangement.
    """
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== ORGANIZE SEATING ==={Colors.RESET}\n")
    print(f"Current input file: {Colors.BLUE}{openspace.input_file}{Colors.RESET}")
    print(f"\n{Colors.GREEN}1.{Colors.RESET} Use current input file")
    print(f"{Colors.GREEN}2.{Colors.RESET} Use different file")

    choice = input("\nEnter your choice (1-2): ")

    if choice == "1":
        input_file = openspace.input_file
    else:
        input_file = input("Enter input file path: ").strip()
        if not input_file:
            input_file = openspace.input_file

    try:
        colleagues = FileUtils.load_colleagues(input_file)
        print(f"\n{Colors.BLUE}Loaded {len(colleagues)} colleagues{Colors.RESET}")

        openspace.organize(colleagues)
        openspace.store(state_file)

        print(
            f"\n{Colors.GREEN}Seating arrangement organized and saved to {state_file}{Colors.RESET}"
        )
        print(
            f"Seated: {Colors.GREEN}{openspace.get_seated_count()}{Colors.RESET}, Unseated: {Colors.YELLOW}{len(openspace.unseated)}{Colors.RESET}"
        )
    except FileNotFoundError:
        print(f"\n{Colors.RED}Error: File '{input_file}' not found!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")

    input("\nPress Enter to continue...")


def add_colleague_menu(openspace: Openspace, state_file: str) -> None:
    """
    Add a colleague to the room.

    :param openspace: The Openspace instance to add a colleague to.
    :param state_file: A str path to the state file for saving the arrangement.
    """
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== ADD COLLEAGUE ==={Colors.RESET}\n")

    name = input("Enter colleague name: ").strip()
    if not name:
        print(f"{Colors.RED}Name cannot be empty!{Colors.RESET}")
        input("\nPress Enter to continue...")
        return

    # Add to input file first
    added_to_file = FileUtils.add_colleague_to_file(openspace.input_file, name)
    if added_to_file:
        print(f"{Colors.GREEN}{name} added to {openspace.input_file}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}{name} already exists in {openspace.input_file}{Colors.RESET}")

    # Try to seat them
    if openspace.add_colleague(name):
        print(f"{Colors.GREEN}{name} has been seated successfully!{Colors.RESET}")
        openspace.store(state_file)
        print(f"Updated arrangement saved to {state_file}")
    else:
        print(
            f"{Colors.YELLOW}{name} could not be seated (no free seats available).{Colors.RESET}"
        )
        print(f"{name} has been added to the unseated list.")
        openspace.store(state_file)

    input("\nPress Enter to continue...")


def add_table_menu(openspace: Openspace, state_file: str) -> None:
    """
    Add a table to the room.

    :param openspace: The Openspace instance to add a table to.
    :param state_file: A str path to the state file for saving the arrangement.
    """
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== ADD TABLE ==={Colors.RESET}\n")

    print(f"Current tables: {Colors.BLUE}{openspace.number_of_tables}{Colors.RESET}")
    confirm = input(
        f"Add a new table with capacity {openspace.table_capacity}? (y/n): "
    )

    if confirm.lower() == "y":
        openspace.add_table()
        print(
            f"\n{Colors.GREEN}Table added! New total: {openspace.number_of_tables} tables{Colors.RESET}"
        )
        openspace.store(state_file)
        print(f"Updated arrangement saved to {state_file}")
    else:
        print(f"\n{Colors.YELLOW}Table not added.{Colors.RESET}")

    input("\nPress Enter to continue...")


def manage_preferences(openspace: Openspace, state_file: str) -> None:
    """
    Manage seating preferences.

    :param openspace: The Openspace instance to manage preferences for.
    :param state_file: A str path to the state file for saving the arrangement.
    """
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== MANAGE PREFERENCES ==={Colors.RESET}\n")
    print(f"{Colors.GREEN}1.{Colors.RESET} Add whitelist preference (sit with someone)")
    print(f"{Colors.GREEN}2.{Colors.RESET} Add blacklist preference (avoid someone)")
    print(f"{Colors.GREEN}3.{Colors.RESET} View current preferences")
    print(f"{Colors.GREEN}4.{Colors.RESET} Back to main menu")

    choice = input("\nEnter your choice (1-4): ")

    if choice == "1":
        person = input("\nEnter person name: ").strip()
        target = input("Enter who they want to sit with: ").strip()
        if person and target:
            openspace.set_preference(person, "whitelist", target)
            openspace.store(state_file)
            print(
                f"\n{Colors.GREEN}Preference added: {person} wants to sit with {target}{Colors.RESET}"
            )
            print(f"Preferences saved to {state_file}")
        else:
            print(f"\n{Colors.RED}Invalid input!{Colors.RESET}")
    elif choice == "2":
        person = input("\nEnter person name: ").strip()
        target = input("Enter who they want to avoid: ").strip()
        if person and target:
            openspace.set_preference(person, "blacklist", target)
            openspace.store(state_file)
            print(
                f"\n{Colors.GREEN}Preference added: {person} wants to avoid {target}{Colors.RESET}"
            )
            print(f"Preferences saved to {state_file}")
        else:
            print(f"\n{Colors.RED}Invalid input!{Colors.RESET}")
    elif choice == "3":
        print(f"\n{Colors.YELLOW}{Colors.BOLD}=== WHITELIST ==={Colors.RESET}")
        if openspace.preferences["whitelist"]:
            for person, targets in openspace.preferences["whitelist"].items():
                print(
                    f"{Colors.GREEN}{person}{Colors.RESET} wants to sit with: {', '.join(targets)}"
                )
        else:
            print("No whitelist preferences set.")

        print(f"\n{Colors.YELLOW}{Colors.BOLD}=== BLACKLIST ==={Colors.RESET}")
        if openspace.preferences["blacklist"]:
            for person, targets in openspace.preferences["blacklist"].items():
                print(
                    f"{Colors.RED}{person}{Colors.RESET} wants to avoid: {', '.join(targets)}"
                )
        else:
            print("No blacklist preferences set.")

    if choice in ["1", "2", "3"]:
        input("\nPress Enter to continue...")


def show_statistics(openspace: Openspace) -> None:
    """
    Display room statistics.

    :param openspace: The Openspace instance containing the seating arrangement.
    """
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}ROOM STATISTICS{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")

    total_seats = openspace.get_total_seats()
    people_seated = openspace.get_seated_count()
    available_seats = openspace.get_remaining_seats()
    people_alone = openspace.get_people_alone_count()

    print(f"\n{Colors.BLUE}Total seats:{Colors.RESET}       {total_seats}")
    print(f"{Colors.GREEN}People seated:{Colors.RESET}     {people_seated}")
    print(f"{Colors.YELLOW}Available seats:{Colors.RESET}   {available_seats}")
    print(f"{Colors.MAGENTA}People alone:{Colors.RESET}      {people_alone}")

    if openspace.unseated:
        print(
            f"\n{Colors.RED}Unseated people:{Colors.RESET}   {len(openspace.unseated)}"
        )
        print(f"{Colors.RED}Unseated colleagues:{Colors.RESET}")
        for name in openspace.unseated:
            print(f"  - {name}")

    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    input("\nPress Enter to continue...")


def show_arrangement(openspace: Openspace) -> None:
    """
    Display current seating arrangement.

    :param openspace: The Openspace instance containing the seating arrangement.
    """
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}CURRENT SEATING ARRANGEMENT{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}\n")

    openspace.display()

    # Display unseated people if any
    if openspace.unseated:
        print(f"\n{Colors.RED}{Colors.BOLD}UNSEATED COLLEAGUES:{Colors.RESET}")
        print(f"{Colors.RED}{'=' * 50}{Colors.RESET}")
        for name in openspace.unseated:
            print(f"{Colors.RED}  - {name}{Colors.RESET}")
        print(f"{Colors.RED}{'=' * 50}{Colors.RESET}")

    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    input("\nPress Enter to continue...")


def main() -> None:
    """
    Main function to organize the openspace seating arrangement.

    Provides an interactive menu system for managing openspace seating including
    configuration, organizing seats, adding colleagues and tables, and viewing statistics.
    """

    STATE_FILE = "openspace_state.json"

    # Try to load existing state
    openspace = Openspace(6, 4)  # Default values
    state_loaded = openspace.load_from_file(STATE_FILE)

    if state_loaded:
        # Try to load all colleagues and check who isn't seated yet
        try:
            all_colleagues = FileUtils.load_colleagues(openspace.input_file)

            # Get currently seated people
            seated_people = set()
            for table in openspace.tables:
                for seat in table.seats:
                    if not seat.free:
                        seated_people.add(seat.occupant)

            # Add people who aren't seated to unseated list
            for colleague in all_colleagues:
                if colleague not in seated_people and colleague not in openspace.unseated:
                    openspace.unseated.append(colleague)

            print(f"Loaded existing session from {STATE_FILE}")
        except FileNotFoundError:
            pass  # No colleagues file yet, that's okay
    else:
        print(f"No previous session found. Starting fresh.")

    clear_terminal()
    print(
        f"{Colors.GREEN}{Colors.BOLD}Welcome to the Openspace Seating Organizer!{Colors.RESET}"
    )

    while True:
        display_menu(openspace)
        choice = input(
            f"\n{Colors.CYAN}Enter your choice (1-9): {Colors.RESET}"
        ).strip()

        if choice == "1":
            config_changed = configure_room(openspace)
            # Recreate openspace if configuration changed
            if config_changed:
                print(f"\n{Colors.YELLOW}Room dimensions changed. Recreating tables...{Colors.RESET}")
                openspace.tables = [Table(openspace.table_capacity) for _ in range(openspace.number_of_tables)]

                # Try to migrate people from old arrangement if it exists
                try:
                    all_colleagues = FileUtils.load_colleagues(openspace.input_file)
                    # Put all colleagues in unseated list - they'll need to be re-organized
                    openspace.unseated = all_colleagues.copy()
                    print(f"{Colors.GREEN}New openspace created with {openspace.number_of_tables} tables of capacity {openspace.table_capacity}{Colors.RESET}")
                    print(f"{Colors.YELLOW}All colleagues moved to unseated list. Please re-organize seating.{Colors.RESET}")
                except FileNotFoundError:
                    print(f"{Colors.GREEN}New openspace created with {openspace.number_of_tables} tables of capacity {openspace.table_capacity}{Colors.RESET}")

                # Save the new configuration
                openspace.store(STATE_FILE)
                input("\nPress Enter to continue...")

        elif choice == "2":
            organize_seating(openspace, STATE_FILE)

        elif choice == "3":
            add_colleague_menu(openspace, STATE_FILE)

        elif choice == "4":
            add_table_menu(openspace, STATE_FILE)

        elif choice == "5":
            clear_terminal()
            print(
                f"\n{Colors.CYAN}{Colors.BOLD}=== RE-ORGANIZE SEATING ==={Colors.RESET}\n"
            )
            print(
                f"{Colors.YELLOW}This will shuffle all currently seated people.{Colors.RESET}"
            )
            confirm = input("Continue? (y/n): ")
            if confirm.lower() == "y":
                # Get all currently seated people
                all_people = []
                for table in openspace.tables:
                    for seat in table.seats:
                        if not seat.free:
                            all_people.append(seat.occupant)
                all_people.extend(openspace.unseated)

                # Re-organize
                openspace.organize(all_people)
                openspace.store(STATE_FILE)
                print(
                    f"\n{Colors.GREEN}Seating re-organized and saved to {STATE_FILE}{Colors.RESET}"
                )
            else:
                print(f"\n{Colors.YELLOW}Re-organization cancelled.{Colors.RESET}")
            input("\nPress Enter to continue...")

        elif choice == "6":
            manage_preferences(openspace, STATE_FILE)

        elif choice == "7":
            show_arrangement(openspace)

        elif choice == "8":
            show_statistics(openspace)

        elif choice == "9":
            # Save state before exiting
            openspace.store(STATE_FILE)
            clear_terminal()
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}Thank you for using the Openspace Seating Organizer!{Colors.RESET}"
            )
            print(f"{Colors.CYAN}Session saved. Goodbye!{Colors.RESET}\n")
            break

        else:
            print(
                f"\n{Colors.RED}Invalid choice. Please enter a number between 1 and 9.{Colors.RESET}"
            )
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()


"""
=== SETUP & CONFIGURATION ===
1. Configure room (tables, capacity, load/save config)
2. Organize initial seating arrangement

=== DYNAMIC CHANGES ===
3. Add a colleague (late arrival)
4. Add a table
5. Re-organize seating

=== PREFERENCES ===
6. Manage seating preferences (white/blacklist)

=== VIEW INFO ===
7. See current arrangement
8. See room statistics
9. Exit
"""
