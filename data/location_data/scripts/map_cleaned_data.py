import pandas as pd
import os


def RemoveIllegalChars(input):
    return (
        str(input)
        .replace('"', "")
        .replace("'", "")
        .replace("{", "")
        .replace("}", "")
        .replace("[", "")
        .replace("]", "")
        .replace(".", "")
    )


merged = pd.read_csv(os.getcwd() + "/location_data/allmerged.csv")

# Drop index columns
#merged.drop(merged.columns[[0]], axis=1, inplace=True)

# SCENE MAP
# Get all rows with scenes
only_scenes_df = merged[merged["sLabel"].notnull()]

# Create scene map
scene_map = only_scenes_df[["tconst", "sconst"]]

# Save scene map
scene_map.to_excel("location_data/converted_data/scene_map.xlsx", index=False)

# Save sample
scene_map.head(10).to_csv(
    "location_data/converted_data/samples/scene_map_sample.csv", index=False
)


# LOCATION MAP
# Get all rows WITHOUT scenes
no_scenes_df = merged[~merged["sLabel"].notnull()]

# Create scene map
location_map = no_scenes_df[["tconst", "lconst"]]

# Save scene map
location_map.to_excel("location_data/converted_data/location_map.xlsx", index=False)

# Save sample
location_map.head(10).to_csv(
    "location_data/converted_data/samples/location_map_sample.csv", index=False
)


# SCENE INFO
# Get all rows with scenes
only_scenes_df = merged[merged["sLabel"].notnull()]

# Create scene info
scene_info = only_scenes_df[["sconst", "sLabel", "lconst"]]

# Remove some leftover invalid characters
scene_info["sLabel"] = scene_info["sLabel"].apply(RemoveIllegalChars)

# Save scene info
scene_info.to_excel("location_data/converted_data/scene_info.xlsx", index=False)

# Save sample
scene_info.head(10).to_csv(
    "location_data/converted_data/samples/scene_info_sample.csv", index=False
)


# LOCATION INFO
# Get columns with location info
location_info = merged[["lconst", "lLabel", "lAltLabel", "lat", "long"]]

# Save location info
location_info.to_excel("location_data/converted_data/location_info.xlsx", index=False)

# Save sample
location_info.head(10).to_csv(
    "location_data/converted_data/samples/location_info_sample.csv", index=False
)
