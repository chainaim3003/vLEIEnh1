import json

# from scripts.format_cesr import format_cesr
# cesr = exec("curl -s http://witness-demo:5642/oobi/EJcceEYdyHdynNaztmRgWkOZ86MIgFqj8gr9ML878o3x/witness")
# print(format_cesr(cesr))

def format_cesr(stream_data: str) -> str:
    formatted_parts = []
    current_pos = 0
    stream_len = len(stream_data)
    event_counter = 1
    decoder = json.JSONDecoder()

    while current_pos < stream_len:
        # Find the start of the JSON object
        # It should be the first non-whitespace char if current_pos is at a message boundary
        temp_pos = current_pos
        while temp_pos < stream_len and stream_data[temp_pos].isspace():
            temp_pos += 1
        
        if temp_pos == stream_len: # Only whitespace left
            break

        if stream_data[temp_pos] != '{':
            # Unexpected non-JSON data at the beginning of a supposed message part
            if temp_pos < stream_len:
                formatted_parts.append(f"--- End of Stream ---")
                formatted_parts.append(f"Orphaned or unexpected non-JSON data:")
                formatted_parts.append(stream_data[temp_pos:])
            break
        
        current_pos = temp_pos

        # Decode the JSON object
        try:
            json_obj, json_end_idx_in_slice = decoder.raw_decode(stream_data[current_pos:])
            abs_json_end_idx = current_pos + json_end_idx_in_slice
        except json.JSONDecodeError as e:
            formatted_parts.append(f"--- Error ---")
            formatted_parts.append(f"Failed to decode JSON object starting at position {current_pos}: {e}")
            formatted_parts.append("Problematic data snippet:")
            formatted_parts.append(stream_data[current_pos : current_pos + 200])
            break 

        try:
            formatted_json = json.dumps(json_obj, indent=2, ensure_ascii=False)
        except TypeError as e:
            formatted_parts.append(f"--- Error ---")
            formatted_parts.append(f"Failed to serialize JSON object to string: {e}")
            formatted_parts.append(f"Original Object: {json_obj}")
            abs_json_end_idx = current_pos + len(stream_data[current_pos:abs_json_end_idx]) # Fallback if raw_decode was tricky

        if "formatted_json" in locals() and formatted_json:
            formatted_parts.append(f"Event {event_counter}:")
            formatted_parts.append("JSON:")
            formatted_parts.append(formatted_json)
            del formatted_json # clean up for next iteration


        attachment_start_pos = abs_json_end_idx
        
        next_json_obj_start_pos = -1
        if attachment_start_pos < stream_len:
            # Find the start of the next JSON object ('{') to determine the end of the current attachment
            # This assumes attachments do not contain '{' that could be misinterpreted as start of new JSON.
            # KERI attachments are usually Base64URL so this is generally safe.
            
            # Scan for the next '{' that is likely part of a new KERI event "v" field
            # A simple find might be too naive if attachments could contain '{'.
            # For CESR, events are concatenated. Attachments follow their event.
            # So, anything after the current JSON up to the *next* valid JSON start is an attachment.
            
            # Let's search for '{"v":"KERI10JSON' or '{"v":"ACDC10JSON'
            # to be more specific than just '{'.
            # The provided rpy also uses KERI10JSON.
            
            search_offset = attachment_start_pos
            # Try to find '{"v":', as it's a common pattern for KERI message starts
            potential_next_json_start = stream_data.find('{"v":', search_offset)

            if potential_next_json_start != -1:
                 # Check if it's one of the known KERI message types to be more certain
                if stream_data[potential_next_json_start:].startswith('{"v":"KERI10JSON') or \
                   stream_data[potential_next_json_start:].startswith('{"v":"ACDC10JSON'):
                    next_json_obj_start_pos = potential_next_json_start
                else: # Found '{"v":' but not a full KERI/ACDC prefix, might be in an attachment. Search further.
                    safer_next_json_start = stream_data.find('{"v":"KERI10JSON', search_offset)
                    if safer_next_json_start != -1:
                        next_json_obj_start_pos = safer_next_json_start
                    # else, no other KERI10JSON found.
                    # ACDC check can be added if necessary but not in this sample stream as events.
            # else, no '{"v":' found, so this is the last message.


        attachment_string = ""
        if next_json_obj_start_pos != -1 and next_json_obj_start_pos >= attachment_start_pos :
            attachment_string = stream_data[attachment_start_pos:next_json_obj_start_pos]
            current_pos = next_json_obj_start_pos 
        else:
            attachment_string = stream_data[attachment_start_pos:]
            current_pos = stream_len 

        stripped_attachment = attachment_string.strip()
        if stripped_attachment:
            formatted_parts.append("Attachment:")
            formatted_parts.append(stripped_attachment)
        
        formatted_parts.append("-" * 60) # Increased separator width
        event_counter += 1
        
    return "\n".join(formatted_parts)

