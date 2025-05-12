#!/bin/sh

scons platform=android target=template_release module_mono_enabled=yes arch=arm32
scons platform=android target=template_release module_mono_enabled=yes arch=arm64 generate_apk=yes
scons platform=android target=template_release module_mono_enabled=yes arch=x86_32
scons platform=android target=template_release module_mono_enabled=yes arch=x86_64 generate_apk=yes

scons platform=android target=template_debug module_mono_enabled=yes arch=arm32
scons platform=android target=template_debug module_mono_enabled=yes arch=arm64 generate_apk=yes
scons platform=android target=template_debug module_mono_enabled=yes arch=x86_32
scons platform=android target=template_debug module_mono_enabled=yes arch=x86_64 generate_apk=yes

