#!/bin/bash

# Define paths
SRC="/Users/artemancikov/Desktop/practical-work-new/reducer/generator_source"
DEST="/Users/artemancikov/Desktop/practical-work-new/reducer/generator_modified"

# Delete everything from the destination directory
rm -rf "$DEST"/*

# Copy everything from the source to the destination, preserving structure
cp -a "$SRC"/. "$DEST"/

