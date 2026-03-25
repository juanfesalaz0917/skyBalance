"""Minimal backend entry point for manual smoke checks."""

from models.Flight import Flight


def main():
    """Create a sample flight and print its serialized view."""
    flight = Flight()
    print(flight.toString())


if __name__ == "__main__":
    main()


