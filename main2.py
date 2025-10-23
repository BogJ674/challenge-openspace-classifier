from utils.openspace import Openspace
from utils.file_utils import FileUtils
import sys
import os


def clear_terminal():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_menu():
    """Display the main menu."""
    print("\n" + "=" * 50)
    print("OPENSPACE SEATING ORGANIZER")
    print("=" * 50)
    print("\n=== SETUP & CONFIGURATION ===")
    print("1. Configure room (tables, capacity, load/save config)")
    print("2. Organize initial seating arrangement")
    print("\n=== DYNAMIC CHANGES ===")
    print("3. Add a colleague (late arrival)")
    print("4. Add a table")
    print("5. Re-organize seating")
    print("\n=== PREFERENCES ===")
    print("6. Manage seating preferences (white/blacklist)")
    print("\n=== VIEW INFO ===")
    print("7. See current arrangement")
    print("8. See room statistics")
    print("\n9. Exit")
    print("=" * 50)


def configure_room(config):
    """Configure room setup."""
    clear_terminal()
    print("\n=== ROOM CONFIGURATION ===\n")
    print("1. Load configuration from config.json")
    print("2. Set custom configuration")
    print("3. Save current configuration to config.json")
    print("4. Back to main menu")

    choice = input("\nEnter your choice (1-4): ")

    if choice == '1':
        config = FileUtils.load_config("config.json")
        print(f"\nConfiguration loaded successfully!")
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

            print("\nConfiguration updated successfully!")
            input("Press Enter to continue...")
        except ValueError:
            print("\nInvalid input! Configuration not changed.")
            input("Press Enter to continue...")
        return config
    elif choice == '3':
        import json
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("\nConfiguration saved to config.json!")
        input("Press Enter to continue...")
        return config
    else:
        return config


def organize_seating(openspace, config):
    """Organize initial seating arrangement."""
    clear_terminal()
    print("\n=== ORGANIZE SEATING ===\n")
    print("1. Use default config from config.json")
    print("2. Provide custom parameters")

    choice = input("\nEnter your choice (1-2): ")

    if choice == '1':
        input_file = config['input_file']
    else:
        input_file = input("Enter input file path: ").strip()
        if not input_file:
            input_file = config['input_file']

    try:
        colleagues = FileUtils.load_colleagues(input_file)
        print(f"\nLoaded {len(colleagues)} colleagues")

        openspace.organize(colleagues)
        openspace.store(config['output_file'])

        print(f"\nSeating arrangement organized and saved to {config['output_file']}")
        print(f"Seated: {openspace.get_seated_count()}, Unseated: {len(openspace.unseated)}")
    except FileNotFoundError:
        print(f"\nError: File '{input_file}' not found!")
    except Exception as e:
        print(f"\nError: {e}")

    input("\nPress Enter to continue...")


def add_colleague_menu(openspace, config):
    """Add a colleague to the room."""
    clear_terminal()
    print("\n=== ADD COLLEAGUE ===\n")

    name = input("Enter colleague name: ").strip()
    if not name:
        print("Name cannot be empty!")
        input("\nPress Enter to continue...")
        return

    if openspace.add_colleague(name):
        print(f"\n{name} has been seated successfully!")
        openspace.store(config['output_file'])
        print(f"Updated arrangement saved to {config['output_file']}")
    else:
        print(f"\n{name} could not be seated (no free seats available).")
        print(f"{name} has been added to the unseated list.")

    input("\nPress Enter to continue...")


def add_table_menu(openspace, config):
    """Add a table to the room."""
    clear_terminal()
    print("\n=== ADD TABLE ===\n")

    print(f"Current tables: {openspace.number_of_tables}")
    confirm = input(f"Add a new table with capacity {openspace.table_capacity}? (y/n): ")

    if confirm.lower() == 'y':
        openspace.add_table()
        print(f"\nTable added! New total: {openspace.number_of_tables} tables")
        openspace.store(config['output_file'])
        print(f"Updated arrangement saved to {config['output_file']}")
    else:
        print("\nTable not added.")

    input("\nPress Enter to continue...")


def manage_preferences(openspace):
    """Manage seating preferences."""
    clear_terminal()
    print("\n=== MANAGE PREFERENCES ===\n")
    print("1. Add whitelist preference (sit with someone)")
    print("2. Add blacklist preference (avoid someone)")
    print("3. View current preferences")
    print("4. Back to main menu")

    choice = input("\nEnter your choice (1-4): ")

    if choice == '1':
        person = input("\nEnter person name: ").strip()
        target = input("Enter who they want to sit with: ").strip()
        if person and target:
            openspace.set_preference(person, "whitelist", target)
            print(f"\nPreference added: {person} wants to sit with {target}")
        else:
            print("\nInvalid input!")
    elif choice == '2':
        person = input("\nEnter person name: ").strip()
        target = input("Enter who they want to avoid: ").strip()
        if person and target:
            openspace.set_preference(person, "blacklist", target)
            print(f"\nPreference added: {person} wants to avoid {target}")
        else:
            print("\nInvalid input!")
    elif choice == '3':
        print("\n=== WHITELIST ===")
        if openspace.preferences['whitelist']:
            for person, targets in openspace.preferences['whitelist'].items():
                print(f"{person} wants to sit with: {', '.join(targets)}")
        else:
            print("No whitelist preferences set.")

        print("\n=== BLACKLIST ===")
        if openspace.preferences['blacklist']:
            for person, targets in openspace.preferences['blacklist'].items():
                print(f"{person} wants to avoid: {', '.join(targets)}")
        else:
            print("No blacklist preferences set.")

    if choice in ['1', '2', '3']:
        input("\nPress Enter to continue...")


def show_statistics(openspace):
    """Display room statistics."""
    clear_terminal()
    print("\n" + "=" * 50)
    print("ROOM STATISTICS")
    print("=" * 50)

    total_seats = openspace.get_total_seats()
    people_seated = openspace.get_seated_count()
    available_seats = openspace.get_remaining_seats()
    people_alone = openspace.get_people_alone_count()

    print(f"\nTotal seats:       {total_seats}")
    print(f"People seated:     {people_seated}")
    print(f"Available seats:   {available_seats}")
    print(f"People alone:      {people_alone}")

    if openspace.unseated:
        print(f"\nUnseated people:   {len(openspace.unseated)}")
        print("Unseated colleagues:")
        for name in openspace.unseated:
            print(f"  - {name}")

    print("=" * 50)
    input("\nPress Enter to continue...")


def show_arrangement(openspace):
    """Display current seating arrangement."""
    clear_terminal()
    print("\n" + "=" * 50)
    print("CURRENT SEATING ARRANGEMENT")
    print("=" * 50 + "\n")

    openspace.display()

    print("=" * 50)
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
    print("Welcome to the Openspace Seating Organizer!")

    while True:
        display_menu()
        choice = input("\nEnter your choice (1-9): ").strip()

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
            print("\n=== RE-ORGANIZE SEATING ===\n")
            print("This will shuffle all currently seated people.")
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
                print(f"\nSeating re-organized and saved to {config['output_file']}")
            else:
                print("\nRe-organization cancelled.")
            input("\nPress Enter to continue...")

        elif choice == '6':
            manage_preferences(openspace)

        elif choice == '7':
            show_arrangement(openspace)

        elif choice == '8':
            show_statistics(openspace)

        elif choice == '9':
            clear_terminal()
            print("\nThank you for using the Openspace Seating Organizer!")
            print("Goodbye!\n")
            break

        else:
            print("\nInvalid choice. Please enter a number between 1 and 9.")
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
