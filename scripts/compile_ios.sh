#!/bin/sh
scons p=ios target=template_debug module_mono_enabled=yes
scons p=ios target=template_release module_mono_enabled=yes

scons p=ios target=template_debug ios_simulator=yes arch=x86_64 module_mono_enabled=yes
scons p=ios target=template_debug ios_simulator=yes arch=arm64 module_mono_enabled=yes

cp -r misc/dist/ios_xcode ./bin

cp bin/libgodot.ios.template_debug.arm64.a bin/ios_xcode/libgodot.ios.debug.xcframework/ios-arm64/libgodot.a
lipo -create bin/libgodot.ios.template_debug.arm64.simulator.a bin/libgodot.ios.template_debug.x86_64.simulator.a -output bin/ios_xcode/libgodot.ios.debug.xcframework/ios-arm64_x86_64-simulator/libgodot.a

cp bin/libgodot.ios.template_release.arm64.a bin/ios_xcode/libgodot.ios.release.xcframework/ios-arm64/libgodot.a
lipo -create bin/libgodot.ios.template_release.arm64.simulator.a bin/libgodot.ios.template_release.x86_64.simulator.a -output bin/ios_xcode/libgodot.ios.release.xcframework/ios-arm64_x86_64-simulator/libgodot.a

cp -r /usr/local/lib/MoltenVK.xcframework bin/ios_xcode/

cd bin/ios_xcode
zip -vr ../ios.zip .
cd ../../