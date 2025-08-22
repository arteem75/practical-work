#!/bin/bash

SRC="reducer/final-jdk-source"
DEST="reducer/final-jdk-modified"

# Delete everything from the destination directory
rm -rf "$DEST"/*

# Copy everything from the source to the destination, preserving structure
cp -a "$SRC"/. "$DEST"/