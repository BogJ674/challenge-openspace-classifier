class Seat:
    """
    represents the seat which could be occupied by a person

    :attr free (bool): if the seat is free or not
    :attr occupant (str): who is occupying the seat"""

    def __init__(self) -> None:
        self.free: bool = True
        self.occupant: str = ""
    
    def set_occupant(self, name: str) -> None:
        """Assigns an occupant to the seat if it is free.
        
        :param name: name of the occupant to assign to the seat.
        :return: None"""
        if self.free:
            self.occupant = name
            self.free = False
        else:
            print("Seat is already occupied.")
    
    def remove_occupant(self) -> str | None:
        """Removes the occupant from the seat and returns their name.
        
        :return: name of the removed occupant or None if the seat was already free."""
        if not self.free:
            name = self.occupant
            self.occupant = ""
            self.free = True
            return name
        else:
            print("Seat is already free.")
            return None
        
class Table:
    """
    Class to represent a table with multiple seats.
        
    :attr seats (list[Seat]): a list of Seat objects at the table.
    :attr capacity (int): representing the number of seats at the table."""

    def __init__(self, capacity: int) -> None:
        self.capacity: int = capacity
        self.seats: list[Seat] = [Seat() for _ in range(capacity)]
    
    def has_free_spot(self) -> bool:
        """Checks if there is at least one free seat at the table.
        
        :return: True if there is a free seat, False otherwise."""
        return any(seat.free for seat in self.seats)
    
    def assign_seat(self, name: str) -> None:
        """Assigns a seat to a person if there is a free spot.
        
        :param name: name of the person to assign to a seat.
        :return: None"""
        for seat in self.seats:
            if seat.free:
                seat.set_occupant(name)
                return
        print("No free seats available.")
    
    def left_capacity(self) -> int:
        """Returns the number of free seats left at the table.
        
        :return: number of free seats."""
        return sum(1 for seat in self.seats if seat.free)
    
    def __str__(self) -> str:
        """Returns a string representation of the table and its seats."""
        seat_statuses = [f"Seat {i+1}: {'Free' if seat.free else seat.occupant}" for i, seat in enumerate(self.seats)]
        return "\n".join(seat_statuses)