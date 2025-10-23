from utils.openspace import Openspace
from utils.file_utils import FileUtils


def main():
    """Main function to organize the openspace seating arrangement."""

    # Configuration
    NUMBER_OF_TABLES = 6
    TABLE_CAPACITY = 4
    INPUT_FILE = "new_colleagues.csv"
    OUTPUT_FILE = "output.csv"

    # Load colleagues from CSV file
    print("Loading colleagues from file...")
    colleagues = FileUtils.load_colleagues(INPUT_FILE)
    print(f"Loaded {len(colleagues)} colleagues: {', '.join(colleagues)}")

    # Create openspace with tables
    print(f"\nCreating openspace with {NUMBER_OF_TABLES} tables of {TABLE_CAPACITY} seats each...")
    openspace = Openspace(NUMBER_OF_TABLES, TABLE_CAPACITY)

    # Organize seating
    print("\nOrganizing seating arrangement...")
    openspace.organize(colleagues)

    # Display the arrangement
    print("\n" + "=" * 40)
    print("SEATING ARRANGEMENT")
    print("=" * 40)
    openspace.display()

    # Store the arrangement to file
    print(f"\nStoring seating arrangement to {OUTPUT_FILE}...")
    openspace.store(OUTPUT_FILE)
    print(f"Successfully saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
