#!/bin/sh

scons platform=macos module_mono_enabled=yes target=template_debug arch=arm64
scons platform=macos module_mono_enabled=yes target=template_release arch=arm64
scons platform=macos module_mono_enabled=yes target=template_debug arch=x86_64
scons platform=macos module_mono_enabled=yes target=template_release arch=x86_64 generate_bundle=yes