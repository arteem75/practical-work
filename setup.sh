#!/bin/bash

# Define paths
SRC="/Users/artemancikov/Desktop/practical-work-new/reducer/jdk-bugs-source"
DEST="/Users/artemancikov/Desktop/practical-work-new/reducer/jdk-bugs-modified"

# Delete everything from the destination directory
rm -rf "$DEST"/*

# Copy everything from the source to the destination, preserving structure
cp -a "$SRC"/. "$DEST"/

