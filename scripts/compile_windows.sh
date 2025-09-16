#!/bin/sh

scons platform=windows module_mono_enabled=yes target=template_debug arch=x86_32
scons platform=windows module_mono_enabled=yes target=template_release arch=x86_32
scons platform=windows module_mono_enabled=yes target=template_debug arch=x86_64
scons platform=windows module_mono_enabled=yes target=template_release arch=x86_64

# Don't have access to ARM64 hardware on Windows, also not sure how well supported it is so turned off for now
#scons platform=windows module_mono_enabled=yes target=template_debug arch=arm64
#scons platform=windows module_mono_enabled=yes target=template_release arch=arm64
