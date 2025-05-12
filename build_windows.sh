#!/bin/sh

# Build editor binary
scons p=windows target=editor module_mono_enabled=yes

# Generate glue sources
bin/godot.windows.editor.x86_64.mono --headless --generate-mono-glue modules/mono/glue
# Build .NET assemblies
python ./modules/mono/build_scripts/build_assemblies.py --godot-output-dir ./bin --godot-platform=windows --push-nupkgs-local /c/Users/MegaMiley/Documents/godot/bin/MyLocalNugetSource
