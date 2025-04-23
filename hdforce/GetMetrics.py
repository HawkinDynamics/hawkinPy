# Dependencies -----
import pandas as pd
from .utils import Metrics

# ----------------- #
# Get Metrics


def GetMetrics(test_type=None) -> pd.DataFrame:
    """
    Get the metrics and ids for all the metrics in the system

    Parameters:
    -----------
    test_type : str
        Designate which test metrics to be called
    
    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing the test metrics, with columns:
        - canonicalTestTypeId: The unique identifier for each test type.
        - testTypeName: The name of each metric.
        - id: The unique identifier for each metric.
        - label: The label (common name) for each metric
        - label_unit: The headers of the metrics as they are returned from the API
        - units: Units of measure
        - description: Full description of metric and calculation*
    """
    # Use the globally loaded metric_dictionary DataFrame
    df = Metrics.MetricDictionary()
    
    # Check typeId
    type_ids = {
        "7nNduHeM5zETPjHxvm7s": ["7nNduHeM5zETPjHxvm7s", "Countermovement Jump", "CMJ"],
        "QEG7m7DhYsD6BrcQ8pic": ["QEG7m7DhYsD6BrcQ8pic", "Squat Jump", "SJ"],
        "2uS5XD5kXmWgIZ5HhQ3A": ["2uS5XD5kXmWgIZ5HhQ3A", "Isometric Test", "ISO"],
        "gyBETpRXpdr63Ab2E0V8": ["gyBETpRXpdr63Ab2E0V8", "Drop Jump", "DJ"],
        "5pRSUQVSJVnxijpPMck3": ["5pRSUQVSJVnxijpPMck3", "Free Run", "FREE"],
        "pqgf2TPUOQOQs6r0HQWb": ["pqgf2TPUOQOQs6r0HQWb", "CMJ Rebound", "CMJR"],
        "r4fhrkPdYlLxYQxEeM78": ["r4fhrkPdYlLxYQxEeM78", "Multi Rebound", "MR"],
        "ubeWMPN1lJFbuQbAM97s": ["ubeWMPN1lJFbuQbAM97s", "Weigh In", "WI"],
        "rKgI4y3ItTAzUekTUpvR": ["rKgI4y3ItTAzUekTUpvR", "Drop Landing", "DL"],
        "4KlQgKmBxbOY6uKTLDFL": ["4KlQgKmBxbOY6uKTLDFL", "TS Free Run", "TSFR"],
        "umnEZPgi6zaxuw0KhUpM": ["umnEZPgi6zaxuw0KhUpM", "TS Isometric Test", "TSISO"]
    }
    # Sort test type Id
    for key, values in type_ids.items():
        if test_type in values:
            t_id = key
            df = df[df['canonicalTestTypeId'] == t_id]
            break
    else:
        df = df

    return df

