#!/bin/sh

# Generate glue sources
bin/godot_macos_editor_mono.app/Contents/MacOS/Godot --headless --generate-mono-glue modules/mono/glue

# Build .NET assemblies
python3 ./modules/mono/build_scripts/build_assemblies.py --godot-output-dir ./bin --godot-platform=macos --push-nupkgs-local ~/MyLocalNugetSource
