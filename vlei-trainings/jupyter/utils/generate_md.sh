#!/usr/bin/env bash
cd /app/notebooks

# Array of notebook filenames to exclude from conversion
EXCLUDE_NOTEBOOKS=(
    "000_Table_of_Contents.ipynb"
    "220_10_Integrating_Chainlink_CCID_with_vLEI.ipynb"
)



OUTPUT_DIR="/app/markdown"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Find all notebook files
for notebook in *.ipynb; do
    # Check if the notebook is in the exclusion list
    if [[ " ${EXCLUDE_NOTEBOOKS[@]} " =~ " ${notebook} " ]]; then
        echo "Skipping excluded notebook: $notebook"
        continue
    fi
    

    echo "Converting $notebook to Markdown in $OUTPUT_DIR"
    jupyter nbconvert --to markdown --output-dir="$OUTPUT_DIR" "$notebook"
    
    # Get the generated markdown filename (remove .ipynb extension and add .md)
    md_filename="${notebook%.ipynb}.md"
    md_filepath="$OUTPUT_DIR/$md_filename"
    
    # Remove ANSI color escape sequences from the generated markdown file
    if [[ -f "$md_filepath" ]]; then
        echo "Cleaning ANSI escape sequences from $md_filename"
        # Use sed to remove ANSI escape sequences
        # Pattern matches: \x1b[ followed by any characters until 'm'
        sed -i 's/\x1b\[[0-9;]*[mK]//g' "$md_filepath"
    fi
    
done

echo "Conversion complete."