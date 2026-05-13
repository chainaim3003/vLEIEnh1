#!/usr/bin/env bash
cd /app/notebooks

# Array of notebook filenames to exclude from conversion
EXCLUDE_NOTEBOOKS=(
    "000_Table_of_Contents.ipynb"
    "101_05_Welcome_to_vLEI_Training_-_101.ipynb"
    "101_07_Introduction_to-KERI_ACDC_and_vLEI.ipynb"
    "101_15_Controllers_and_Identifiers.ipynb"
    "101_35_Modes_oobis_and_witnesses.ipynb"
    "101_50_ACDC.ipynb"
    "101_55_Schemas.ipynb"
    "101_75_ACDC_Edges_and_Rules.ipynb"
    "101_85_ACDC_Chained_Credentials_NI2I.ipynb"
    "102_05_KERIA_Signify.ipynb"
    "102_30_Third_Party_Tools.ipynb"
    "103_05_vLEI_Ecosystem.ipynb"
    "220_10_Integrating_Chainlink_CCID_with_vLEI.ipynb"
    "900_05_Known_Issues.ipynb"
)


# Find all notebook files
for notebook in *.ipynb; do
    # Check if the notebook is in the exclusion list
    if [[ " ${EXCLUDE_NOTEBOOKS[@]} " =~ " ${notebook} " ]]; then
        echo "Skipping excluded notebook: $notebook"
        continue
    fi

    echo "Executing $notebook"
    jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 "$notebook"
done

echo "Run complete."
