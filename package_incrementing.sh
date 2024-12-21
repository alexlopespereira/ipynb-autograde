#!/bin/bash

# Extract the current version from the command
current_version="0.0.69" # Replace this with your initial version

# Split the version into its parts (major.minor.patch)
IFS='.' read -r major minor patch <<< "$current_version"

# Increment the patch version
new_patch=$((patch + 1))
new_version="$major.$minor.$new_patch"

# Run the command with the new version
sh ./package.sh "$new_version" "incremental improvements"

# Save the new version (optional: write it to a file to persist)
echo "Version updated to: $new_version"
echo "$new_version" > current_version.txt