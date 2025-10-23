from utils.openspace import Openspace
from utils.file_utils import FileUtils
import sys
import os


# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Regular colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    # Background colors
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'


def clear_terminal():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_menu():
    """Display the main menu."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}OPENSPACE SEATING ORGANIZER{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    print(f"\n{Colors.YELLOW}{Colors.BOLD}=== SETUP & CONFIGURATION ==={Colors.RESET}")
    print(f"{Colors.GREEN}1.{Colors.RESET} Configure room (tables, capacity, load/save config)")
    print(f"{Colors.GREEN}2.{Colors.RESET} Organize initial seating arrangement")
    print(f"\n{Colors.YELLOW}{Colors.BOLD}=== DYNAMIC CHANGES ==={Colors.RESET}")
    print(f"{Colors.GREEN}3.{Colors.RESET} Add a colleague (late arrival)")
    print(f"{Colors.GREEN}4.{Colors.RESET} Add a table")
    print(f"{Colors.GREEN}5.{Colors.RESET} Re-organize seating")
    print(f"\n{Colors.YELLOW}{Colors.BOLD}=== PREFERENCES ==={Colors.RESET}")
    print(f"{Colors.GREEN}6.{Colors.RESET} Manage seating preferences (white/blacklist)")
    print(f"\n{Colors.YELLOW}{Colors.BOLD}=== VIEW INFO ==={Colors.RESET}")
    print(f"{Colors.GREEN}7.{Colors.RESET} See current arrangement")
    print(f"{Colors.GREEN}8.{Colors.RESET} See room statistics")
    print(f"\n{Colors.RED}9.{Colors.RESET} Exit")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")


def configure_room(config):
    """Configure room setup."""
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== ROOM CONFIGURATION ==={Colors.RESET}\n")
    print(f"{Colors.GREEN}1.{Colors.RESET} Load configuration from config.json")
    print(f"{Colors.GREEN}2.{Colors.RESET} Set custom configuration")
    print(f"{Colors.GREEN}3.{Colors.RESET} Save current configuration to config.json")
    print(f"{Colors.GREEN}4.{Colors.RESET} Back to main menu")

    choice = input("\nEnter your choice (1-4): ")

    if choice == '1':
        config = FileUtils.load_config("config.json")
        print(f"\n{Colors.GREEN}Configuration loaded successfully!{Colors.RESET}")
        print(f"Tables: {config['number_of_tables']}, Capacity: {config['table_capacity']}")
        input("\nPress Enter to continue...")
        return config
    elif choice == '2':
        try:
            tables = int(input("Enter number of tables: "))
            capacity = int(input("Enter table capacity: "))
            input_file = input("Enter input file (press Enter for default): ").strip()
            output_file = input("Enter output file (press Enter for default): ").strip()

            config['number_of_tables'] = tables
            config['table_capacity'] = capacity
            if input_file:
                config['input_file'] = input_file
            if output_file:
                config['output_file'] = output_file

            print(f"\n{Colors.GREEN}Configuration updated successfully!{Colors.RESET}")
            input("Press Enter to continue...")
        except ValueError:
            print(f"\n{Colors.RED}Invalid input! Configuration not changed.{Colors.RESET}")
            input("Press Enter to continue...")
        return config
    elif choice == '3':
        import json
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        print(f"\n{Colors.GREEN}Configuration saved to config.json!{Colors.RESET}")
        input("Press Enter to continue...")
        return config
    else:
        return config


def organize_seating(openspace, config):
    """Organize initial seating arrangement."""
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== ORGANIZE SEATING ==={Colors.RESET}\n")
    print(f"{Colors.GREEN}1.{Colors.RESET} Use default config from config.json")
    print(f"{Colors.GREEN}2.{Colors.RESET} Provide custom parameters")

    choice = input("\nEnter your choice (1-2): ")

    if choice == '1':
        input_file = config['input_file']
    else:
        input_file = input("Enter input file path: ").strip()
        if not input_file:
            input_file = config['input_file']

    try:
        colleagues = FileUtils.load_colleagues(input_file)
        print(f"\n{Colors.BLUE}Loaded {len(colleagues)} colleagues{Colors.RESET}")

        openspace.organize(colleagues)
        openspace.store(config['output_file'])

        print(f"\n{Colors.GREEN}Seating arrangement organized and saved to {config['output_file']}{Colors.RESET}")
        print(f"Seated: {Colors.GREEN}{openspace.get_seated_count()}{Colors.RESET}, Unseated: {Colors.YELLOW}{len(openspace.unseated)}{Colors.RESET}")
    except FileNotFoundError:
        print(f"\n{Colors.RED}Error: File '{input_file}' not found!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")

    input("\nPress Enter to continue...")


def add_colleague_menu(openspace, config):
    """Add a colleague to the room."""
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== ADD COLLEAGUE ==={Colors.RESET}\n")

    name = input("Enter colleague name: ").strip()
    if not name:
        print(f"{Colors.RED}Name cannot be empty!{Colors.RESET}")
        input("\nPress Enter to continue...")
        return

    if openspace.add_colleague(name):
        print(f"\n{Colors.GREEN}{name} has been seated successfully!{Colors.RESET}")
        openspace.store(config['output_file'])
        print(f"Updated arrangement saved to {config['output_file']}")
    else:
        print(f"\n{Colors.YELLOW}{name} could not be seated (no free seats available).{Colors.RESET}")
        print(f"{name} has been added to the unseated list.")

    input("\nPress Enter to continue...")


def add_table_menu(openspace, config):
    """Add a table to the room."""
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== ADD TABLE ==={Colors.RESET}\n")

    print(f"Current tables: {Colors.BLUE}{openspace.number_of_tables}{Colors.RESET}")
    confirm = input(f"Add a new table with capacity {openspace.table_capacity}? (y/n): ")

    if confirm.lower() == 'y':
        openspace.add_table()
        print(f"\n{Colors.GREEN}Table added! New total: {openspace.number_of_tables} tables{Colors.RESET}")
        openspace.store(config['output_file'])
        print(f"Updated arrangement saved to {config['output_file']}")
    else:
        print(f"\n{Colors.YELLOW}Table not added.{Colors.RESET}")

    input("\nPress Enter to continue...")


def manage_preferences(openspace):
    """Manage seating preferences."""
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== MANAGE PREFERENCES ==={Colors.RESET}\n")
    print(f"{Colors.GREEN}1.{Colors.RESET} Add whitelist preference (sit with someone)")
    print(f"{Colors.GREEN}2.{Colors.RESET} Add blacklist preference (avoid someone)")
    print(f"{Colors.GREEN}3.{Colors.RESET} View current preferences")
    print(f"{Colors.GREEN}4.{Colors.RESET} Back to main menu")

    choice = input("\nEnter your choice (1-4): ")

    if choice == '1':
        person = input("\nEnter person name: ").strip()
        target = input("Enter who they want to sit with: ").strip()
        if person and target:
            openspace.set_preference(person, "whitelist", target)
            print(f"\n{Colors.GREEN}Preference added: {person} wants to sit with {target}{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}Invalid input!{Colors.RESET}")
    elif choice == '2':
        person = input("\nEnter person name: ").strip()
        target = input("Enter who they want to avoid: ").strip()
        if person and target:
            openspace.set_preference(person, "blacklist", target)
            print(f"\n{Colors.GREEN}Preference added: {person} wants to avoid {target}{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}Invalid input!{Colors.RESET}")
    elif choice == '3':
        print(f"\n{Colors.YELLOW}{Colors.BOLD}=== WHITELIST ==={Colors.RESET}")
        if openspace.preferences['whitelist']:
            for person, targets in openspace.preferences['whitelist'].items():
                print(f"{Colors.GREEN}{person}{Colors.RESET} wants to sit with: {', '.join(targets)}")
        else:
            print("No whitelist preferences set.")

        print(f"\n{Colors.YELLOW}{Colors.BOLD}=== BLACKLIST ==={Colors.RESET}")
        if openspace.preferences['blacklist']:
            for person, targets in openspace.preferences['blacklist'].items():
                print(f"{Colors.RED}{person}{Colors.RESET} wants to avoid: {', '.join(targets)}")
        else:
            print("No blacklist preferences set.")

    if choice in ['1', '2', '3']:
        input("\nPress Enter to continue...")


def show_statistics(openspace):
    """Display room statistics."""
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
        print(f"\n{Colors.RED}Unseated people:{Colors.RESET}   {len(openspace.unseated)}")
        print(f"{Colors.RED}Unseated colleagues:{Colors.RESET}")
        for name in openspace.unseated:
            print(f"  - {name}")

    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    input("\nPress Enter to continue...")


def show_arrangement(openspace):
    """Display current seating arrangement."""
    clear_terminal()
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}CURRENT SEATING ARRANGEMENT{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}\n")

    openspace.display()

    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    input("\nPress Enter to continue...")


def main():
    """Main function to organize the openspace seating arrangement."""

    # Load configuration
    config = FileUtils.load_config("config.json")

    # Initialize openspace
    openspace = Openspace(config['number_of_tables'], config['table_capacity'])

    # Try to load existing arrangement from output file
    if openspace.load_from_file(config['output_file']):
        print(f"Loaded existing arrangement from {config['output_file']}")

    clear_terminal()
    print(f"{Colors.GREEN}{Colors.BOLD}Welcome to the Openspace Seating Organizer!{Colors.RESET}")

    while True:
        display_menu()
        choice = input(f"\n{Colors.CYAN}Enter your choice (1-9): {Colors.RESET}").strip()

        if choice == '1':
            config = configure_room(config)
            # Update openspace if configuration changed
            openspace = Openspace(config['number_of_tables'], config['table_capacity'])
            openspace.load_from_file(config['output_file'])

        elif choice == '2':
            organize_seating(openspace, config)

        elif choice == '3':
            add_colleague_menu(openspace, config)

        elif choice == '4':
            add_table_menu(openspace, config)

        elif choice == '5':
            clear_terminal()
            print(f"\n{Colors.CYAN}{Colors.BOLD}=== RE-ORGANIZE SEATING ==={Colors.RESET}\n")
            print(f"{Colors.YELLOW}This will shuffle all currently seated people.{Colors.RESET}")
            confirm = input("Continue? (y/n): ")
            if confirm.lower() == 'y':
                # Get all currently seated people
                all_people = []
                for table in openspace.tables:
                    for seat in table.seats:
                        if not seat.free:
                            all_people.append(seat.occupant)
                all_people.extend(openspace.unseated)

                # Re-organize
                openspace.organize(all_people)
                openspace.store(config['output_file'])
                print(f"\n{Colors.GREEN}Seating re-organized and saved to {config['output_file']}{Colors.RESET}")
            else:
                print(f"\n{Colors.YELLOW}Re-organization cancelled.{Colors.RESET}")
            input("\nPress Enter to continue...")

        elif choice == '6':
            manage_preferences(openspace)

        elif choice == '7':
            show_arrangement(openspace)

        elif choice == '8':
            show_statistics(openspace)

        elif choice == '9':
            clear_terminal()
            print(f"\n{Colors.GREEN}{Colors.BOLD}Thank you for using the Openspace Seating Organizer!{Colors.RESET}")
            print(f"{Colors.CYAN}Goodbye!{Colors.RESET}\n")
            break

        else:
            print(f"\n{Colors.RED}Invalid choice. Please enter a number between 1 and 9.{Colors.RESET}")
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
