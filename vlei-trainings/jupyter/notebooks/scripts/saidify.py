import json
import os
from keri.core import coring, scheming
import copy # Needed for deepcopy if preferred
from typing import Optional, Dict, Any


# --- Constants ---
DEFAULT_SAID_KEY = coring.Saids.dollar  # Use $id for the top-level schema SAID
DEFAULT_HASH_CODE = coring.MtrDex.Blake3_256
JSON_SCHEMA_ID_KEY = '$id' # Standard key for identifying sub-schemas
PROPERTY_KEYS_TO_PROCESS = ["a", "e", "r"] # Keys whose contents might need SAIDs


# --- Helper Function ---

def _try_calculate_and_set_said(item: dict, hash_code: str):
    """
    Checks if a dictionary item has '$id' and content besides '$id'.
    If so, calculates its SAID using '$id' as the label and updates the item's '$id'.

    Args:
        item: The dictionary to process.
        hash_code: The hash algorithm code (e.g., Blake3_256).
    """
    # Ensure item is a dict and has the $id key
    if not isinstance(item, dict) or JSON_SCHEMA_ID_KEY not in item:
        return # Not applicable for SAID calculation

    # Check if there's content other than the $id key itself
    # Create a shallow copy is enough for this check
    temp_copy_for_check = item.copy()
    del temp_copy_for_check[JSON_SCHEMA_ID_KEY] # Remove $id for the check

    if not temp_copy_for_check:
        return # Skip SAID calculation if no content besides $id

    try:
        # Calculate SAID using $id as the label.
        item_for_saider = item.copy()
        said = coring.Saider(sad=item_for_saider,
                             code=hash_code,
                             label=JSON_SCHEMA_ID_KEY).qb64
        # Update the original item's $id field with the calculated SAID
        item[JSON_SCHEMA_ID_KEY] = said
    except Exception as e:
        # Catch potential errors during SAID calculation (like EmptyMaterialError, though unlikely now)
        original_id = item.get(JSON_SCHEMA_ID_KEY, 'N/A') # Get original $id for logging
        print(f"Warning: Error generating SAID for item with original {JSON_SCHEMA_ID_KEY}='{original_id}'. Error: {e}")



# --- Core Logic ---

def add_saids_to_data(data_dict: dict, said_key: str = DEFAULT_SAID_KEY, hash_code: str = DEFAULT_HASH_CODE) -> dict:
    """
    Adds Self-Addressing Identifiers (SAIDs) to the overall schema and specific sub-schemas.
    Processes specified top-level properties ('a', 'e', 'r') looking for sub-schemas
    within 'oneOf' lists or directly if marked with '$id'.

    Args:
        data_dict: The dictionary (e.g., loaded JSON schema) to process.
        said_key: The dictionary key for the SAID of the *entire* schema (e.g., '$id').
        hash_code: The KERI MtrDex code specifying the hashing algorithm.

    Returns:
        The modified dictionary with SAIDs added.
    """
    # Use deepcopy for safety, ensuring original dict isn't modified until the end
    processed_dict = copy.deepcopy(data_dict)

    # --- Process specific properties for potential sub-schema SAIDs ---
    if 'properties' in processed_dict:
        properties = processed_dict['properties']
        for prop_key in PROPERTY_KEYS_TO_PROCESS:
            if prop_key in properties:
                prop_value = properties[prop_key]

                # Case 1: Direct property value is a dict (potentially with $id)
                # The helper function will check for $id and content
                if isinstance(prop_value, dict):
                     _try_calculate_and_set_said(prop_value, hash_code)

                # Case 2: Property value contains 'oneOf' list
                # Check items within the list
                if isinstance(prop_value, dict) and 'oneOf' in prop_value and isinstance(prop_value['oneOf'], list):
                    for item in prop_value['oneOf']:
                        # Helper function checks if item is dict, has $id, and content
                        _try_calculate_and_set_said(item, hash_code)

    # --- Calculate and add SAID for the entire input dictionary ---
    # Use the overall 'said_key' (e.g., '$id') provided to the function
    dict_copy_for_said = copy.deepcopy(processed_dict) # Use a fresh deep copy for top-level SAID
    try:
        # Keri Saider handles the label exclusion internally based on the 'label' param.
        processed_dict[said_key] = coring.Saider(sad=dict_copy_for_said,
                                                 code=hash_code,
                                                 label=said_key).qb64
    except Exception as e:
        print(f"Warning: Error generating top-level SAID ('{said_key}'): Error: {e}")

    return processed_dict

# --- File Handling ---
def _write_json_file(data: dict, filepath: str, indent: bool = True):
    """ Writes dictionary to JSON file (indented or flat). """
    # (Implementation remains the same as before)
    try:
        output_dir = os.path.dirname(filepath)
        if output_dir:
             os.makedirs(output_dir, exist_ok=True)
        with open(filepath, 'w') as f:
            if indent:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f, indent=None, separators=(',', ':'))
        print(f"Successfully wrote processed data to {filepath}")
    except IOError as e:
        print(f"Error writing JSON to {filepath}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing {filepath}: {e}")


# --- Main Processing Function ---
def process_schema_file(input_filepath: str, output_filepath: str, indent_output: bool = True):
    """
    Reads JSON schema, adds SAIDs, orders keys, writes to output file.
    """
    try:
        with open(input_filepath, 'r') as infile:
            # Load using OrderedDict if precise input order matters before processing
            # original_data = json.load(infile, object_pairs_hook=OrderedDict)
            original_data = json.load(infile)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_filepath}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {input_filepath}: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading {input_filepath}: {e}")
        return

    # Add SAIDs using the refined logic
    data_with_saids = add_saids_to_data(original_data, said_key=DEFAULT_SAID_KEY, hash_code=DEFAULT_HASH_CODE)

    # Schemer processing (Recommended by KERI)
    try:
        # Pass the SAIDified data (which should have $id fields populated)
        schemer = scheming.Schemer(sed=data_with_saids)
        processed_data_from_schemer = schemer.sed
    except Exception as e:
        print(f"Warning: Error creating or using KERI Schemer: {e}")
        print("Proceeding with data after SAID calculation but before Schemer processing.")
        processed_data_from_schemer = data_with_saids # Fallback

    # Write the final data
    _write_json_file(processed_data_from_schemer, output_filepath, indent=indent_output)



def get_schema_said(filepath: str, top_level_key: str = JSON_SCHEMA_ID_KEY) -> str | None:
    """
    Reads a JSON schema file and extracts the value of the specified top-level key,
    which is expected to be the top-most SAID of the schema.

    Args:
        filepath: Path to the input JSON schema file (assumed to be SAIDified).
        top_level_key: The dictionary key at the root level that holds the SAID
                       (defaults to '$id').

    Returns:
        The SAID string if found and is a non-empty string, otherwise None.
        Prints error messages to console for failure cases.
    """
    try:
        # Ensure the file exists before trying to open
        if not os.path.exists(filepath):
             raise FileNotFoundError(f"Input file not found at {filepath}")

        with open(filepath, 'r', encoding='utf-8') as infile:
            data = json.load(infile)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filepath}: {e}")
        return None
    except IOError as e:
        print(f"Error reading file {filepath}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading {filepath}: {e}")
        return None

    # Check if the loaded data is a dictionary
    if not isinstance(data, dict):
        print(f"Error: Expected JSON root to be a dictionary in {filepath}, but found {type(data)}.")
        return None

    # Check if the specified top-level key exists
    if top_level_key not in data:
        print(f"Error: Top-level key '{top_level_key}' not found in the root of {filepath}.")
        return None

    # Get the value associated with the key
    said_value = data[top_level_key]

    # Check if the value is a string
    if not isinstance(said_value, str):
        print(f"Warning: Value for top-level key '{top_level_key}' in {filepath} is not a string (found type: {type(said_value)}). Returning None.")
        return None

    # Check if the string value is empty (SAIDs should not be empty)
    if not said_value:
         print(f"Warning: Value for top-level key '{top_level_key}' in {filepath} is an empty string. Returning None.")
         return None

    return said_value