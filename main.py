from utils.openspace import Openspace
from utils.file_utils import FileUtils
import sys


def main():
    """Main function to organize the openspace seating arrangement."""

    # Configuration
    NUMBER_OF_TABLES = 5
    TABLE_CAPACITY = 5
    OUTPUT_FILE = "output.csv"

    # Get input file from command line argument or use default
    if len(sys.argv) > 1:
        INPUT_FILE = sys.argv[1]
    else:
        INPUT_FILE = "new_colleagues.csv"

    # Load colleagues from CSV file
    print(f"Loading colleagues from file: {INPUT_FILE}")
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

    # Display statistics
    openspace.display_statistics()

    # Store the arrangement to file
    print(f"\nStoring seating arrangement to {OUTPUT_FILE}...")
    openspace.store(OUTPUT_FILE)
    print(f"Successfully saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
