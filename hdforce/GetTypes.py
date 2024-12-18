# Dependencies -----
import pandas as pd

# -------------------- #
# Get Test Types

def GetTypes() -> pd.DataFrame:
    """Get the test type names and IDs.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the test types, with columns:
        - id: The unique identifier for each test type.
        - name: The name of each test type.
        - abbreviation: The abbreviation for each test type.
    """
    test_data = {
        "canonicalId": [
            "7nNduHeM5zETPjHxvm7s", "QEG7m7DhYsD6BrcQ8pic", "2uS5XD5kXmWgIZ5HhQ3A",
            "gyBETpRXpdr63Ab2E0V8", "5pRSUQVSJVnxijpPMck3", "pqgf2TPUOQOQs6r0HQWb",
            "r4fhrkPdYlLxYQxEeM78", "ubeWMPN1lJFbuQbAM97s", "rKgI4y3ItTAzUekTUpvR",
            "4KlQgKmBxbOY6uKTLDFL", "umnEZPgi6zaxuw0KhUpM"
        ],
        "name": [
            "Countermovement Jump", "Squat Jump", "Isometric Test", "Drop Jump",
            "Free Run", "CMJ Rebound", "Multi Rebound", "Weigh In", "Drop Landing",
            "TS Free Run", "TS Isometric Test"
        ],
        "abbreviation": ["CMJ", "SJ", "ISO", "DJ", "FR", "CMJR", "MR", "WI", "DL", "TSFR", "TSISO"]
    }

    return pd.DataFrame(test_data)