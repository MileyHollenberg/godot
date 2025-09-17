import json
import os
import platform
import shutil
import subprocess

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

if os.path.basename(os.getcwd()) != "godot":
    print("This script must be run from the godot root directory via ./scripts/build.py")
    exit(1)

try:
    with open("version.py", "r") as f:
        version_content = f.read()
        MAJOR = eval(next(line.split("=")[1].strip() for line in version_content.splitlines() if "major =" in line))
        MINOR = eval(next(line.split("=")[1].strip() for line in version_content.splitlines() if "minor =" in line))
        PATCH = eval(next(line.split("=")[1].strip() for line in version_content.splitlines() if "patch =" in line))
        STATUS = next(
            line.split("=")[1].strip().strip('"') for line in version_content.splitlines() if "status =" in line
        )
except (FileNotFoundError, StopIteration) as e:
    print(f"Error reading version.py: {e}")
    exit(1)

if PATCH == 0:
    GODOT_VERSION = f"{MAJOR}.{MINOR}.{STATUS}.mono"
else:
    GODOT_VERSION = f"{MAJOR}.{MINOR}.{PATCH}.{STATUS}.mono"

if os.name == "posix":
    if os.uname().sysname == "Darwin":
        try:
            with open(os.path.expanduser("~/Documents/AndroidKeystore/godot.gdkey"), "r") as f:
                os.environ["SCRIPT_AES256_ENCRYPTION_KEY"] = f.read().strip()
        except FileNotFoundError:
            print("Error: godot.gdkey not found at ~/Documents/AndroidKeystore/")
            exit(1)
    else:
        print("Unsupported OS detected, can't retrieve the godot.gdkey")
        exit(1)
elif os.name == "nt":
    try:
        with open(os.path.join("E:/", "AndroidKeystore", "godot.gdkey"), "r") as f:
            os.environ["SCRIPT_AES256_ENCRYPTION_KEY"] = f.read().strip()
    except FileNotFoundError:
        print("Error: godot.gdkey not found at E:\\AndroidKeystore\\")
        exit(1)
else:
    print("Unsupported OS detected.")
    exit(1)


def copyTo(sourceFile, targetDirectory, targetName):
    try:
        os.makedirs(targetDirectory, exist_ok=True)
        subprocess.run(
            [
                "cp",
                "./bin/" + sourceFile,
                os.path.join(targetDirectory, targetName),
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error copying files: {e}")
    except OSError as e:
        print(f"Error creating directories: {e}")


def copyToExportDir(sourceFile, targetName):
    if os.name == "posix" and platform.system() == "Darwin":
        home_dir = os.path.expanduser("~")
        template_dir = os.path.join(
            home_dir, "Library", "Application Support", "Godot", "export_templates", GODOT_VERSION
        )
    elif os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            appdata = os.path.expanduser("~/.config")
        template_dir = os.path.join(appdata, "Godot", "export_templates", GODOT_VERSION)

    copyTo(sourceFile, template_dir, targetName)


def build_windows():
    if os.name == "posix" and os.uname().sysname == "Darwin":
        print("Refusing to build Windows binaries on macOS")
        return

    subprocess.run(
        ["scons", "platform=windows", "module_mono_enabled=yes", "target=template_debug", "arch=x86_32"], check=True
    )
    subprocess.run(
        ["scons", "platform=windows", "module_mono_enabled=yes", "target=template_release", "arch=x86_32"], check=True
    )
    subprocess.run(
        ["scons", "platform=windows", "module_mono_enabled=yes", "target=template_debug", "arch=x86_64"], check=True
    )
    subprocess.run(
        ["scons", "platform=windows", "module_mono_enabled=yes", "target=template_release", "arch=x86_64"], check=True
    )

    copyToExportDir("godot.windows.template_debug.x86_32.mono.console.exe", "windows_debug_x86_32_console.exe")
    copyToExportDir("godot.windows.template_debug.x86_32.mono.exe", "windows_debug_x86_32.exe")
    copyToExportDir("godot.windows.template_debug.x86_64.mono.console.exe", "windows_debug_x86_64_console.exe")
    copyToExportDir("godot.windows.template_debug.x86_64.mono.exe", "windows_debug_x86_64.exe")

    copyToExportDir("godot.windows.template_release.x86_32.mono.console.exe", "windows_release_x86_32_console.exe")
    copyToExportDir("godot.windows.template_release.x86_32.mono.exe", "windows_release_x86_32.exe")
    copyToExportDir("godot.windows.template_release.x86_64.mono.console.exe", "windows_release_x86_64_console.exe")
    copyToExportDir("godot.windows.template_release.x86_64.mono.exe", "windows_release_x86_64.exe")


def build_windows_editor():
    if os.name == "posix" and os.uname().sysname == "Darwin":
        print("Refusing to build Windows binaries on macOS")
        return
    subprocess.run(["scons", "platform=windows", "module_mono_enabled=yes", "target=editor"], check=True)


def build_macos():
    if os.name == "nt":
        print("Refusing to build macOS binaries on Windows")
        return

    subprocess.run(
        ["scons", "platform=macos", "module_mono_enabled=yes", "target=template_debug", "arch=arm64"], check=True
    )
    subprocess.run(
        ["scons", "platform=macos", "module_mono_enabled=yes", "target=template_release", "arch=arm64"], check=True
    )
    subprocess.run(
        ["scons", "platform=macos", "module_mono_enabled=yes", "target=template_debug", "arch=x86_64"], check=True
    )
    subprocess.run(
        [
            "scons",
            "platform=macos",
            "module_mono_enabled=yes",
            "target=template_release",
            "arch=x86_64",
            "generate_bundle=yes",
        ],
        check=True,
    )  # TODO check if the generate_bundle is needed here

    copyToExportDir("godot_macos_mono.zip", "macos.zip")


def build_macos_editor():
    if os.name == "nt":
        print("Refusing to build macOS binaries on Windows")
        return
    subprocess.run(
        ["scons", "platform=macos", "arch=arm64", "target=editor", "module_mono_enabled=yes", "generate_bundle=yes"],
        check=True,
    )


def build_android():
    if os.name == "nt":
        os.environ["JAVA_HOME"] = "C:/Program Files/Java/jdk-17"

    subprocess.run(
        ["scons", "platform=android", "module_mono_enabled=yes", "target=template_release", "arch=arm32"], check=True
    )
    subprocess.run(
        [
            "scons",
            "platform=android",
            "module_mono_enabled=yes",
            "target=template_release",
            "arch=arm64",
            "generate_apk=yes",
        ],
        check=True,
    )
    subprocess.run(
        ["scons", "platform=android", "module_mono_enabled=yes", "target=template_release", "arch=x86_32"], check=True
    )
    subprocess.run(
        [
            "scons",
            "platform=android",
            "module_mono_enabled=yes",
            "target=template_release",
            "arch=x86_64",
            "generate_apk=yes",
        ],
        check=True,
    )

    subprocess.run(
        ["scons", "platform=android", "module_mono_enabled=yes", "target=template_debug", "arch=arm32"], check=True
    )
    subprocess.run(
        [
            "scons",
            "platform=android",
            "module_mono_enabled=yes",
            "target=template_debug",
            "arch=arm64",
            "generate_apk=yes",
        ],
        check=True,
    )
    subprocess.run(
        ["scons", "platform=android", "module_mono_enabled=yes", "target=template_debug", "arch=x86_32"], check=True
    )
    subprocess.run(
        [
            "scons",
            "platform=android",
            "module_mono_enabled=yes",
            "target=template_debug",
            "arch=x86_64",
            "generate_apk=yes",
        ],
        check=True,
    )

    copyToExportDir("android_source.zip", "android_source.zip")
    copyToExportDir("android_monoDebug.apk", "android_debug.apk")
    copyToExportDir("android_monoRelease.apk", "android_release.apk")

    with open("scripts/projects.json") as f:
        d = json.load(f)
        for item in d:
            if "actions" in item and "copy_android_libs" in item["actions"]:
                path = item["macos_path"]
                if os.name == "nt":
                    path = item["windows_path"]

                copyTo(
                    "godot-lib.template_debug.aar",
                    os.path.join(path, "android", "build", "libs", "debug"),
                    "godot-lib.template_debug.aar",
                )
                copyTo(
                    "godot-lib.template_release.aar",
                    os.path.join(path, "android", "build", "libs", "release"),
                    "godot-lib.template_release.aar",
                )


def build_ios():
    if os.name == "nt":
        print("Refusing to build iOS binaries on Windows")
        return

    subprocess.run(["scons", "p=ios", "target=template_debug", "module_mono_enabled=yes"], check=True)
    subprocess.run(["scons", "p=ios", "target=template_release", "module_mono_enabled=yes"], check=True)
    subprocess.run(
        ["scons", "p=ios", "target=template_debug", "ios_simulator=yes", "arch=x86_64", "module_mono_enabled=yes"],
        check=True,
    )
    subprocess.run(
        ["scons", "p=ios", "target=template_debug", "ios_simulator=yes", "arch=arm64", "module_mono_enabled=yes"],
        check=True,
    )

    shutil.copytree("misc/dist/ios_xcode", "bin/ios_xcode", dirs_exist_ok=True)

    os.makedirs("bin/ios_xcode/libgodot.ios.debug.xcframework/ios-arm64", exist_ok=True)
    shutil.copy(
        "bin/libgodot.ios.template_debug.arm64.a", "bin/ios_xcode/libgodot.ios.debug.xcframework/ios-arm64/libgodot.a"
    )

    os.makedirs("bin/ios_xcode/libgodot.ios.debug.xcframework/ios-arm64_x86_64-simulator", exist_ok=True)
    subprocess.run(
        [
            "lipo",
            "-create",
            "bin/libgodot.ios.template_debug.arm64.simulator.a",
            "bin/libgodot.ios.template_debug.x86_64.simulator.a",
            "-output",
            "bin/ios_xcode/libgodot.ios.debug.xcframework/ios-arm64_x86_64-simulator/libgodot.a",
        ],
        check=True,
    )

    os.makedirs("bin/ios_xcode/libgodot.ios.release.xcframework/ios-arm64", exist_ok=True)
    shutil.copy(
        "bin/libgodot.ios.template_release.arm64.a",
        "bin/ios_xcode/libgodot.ios.release.xcframework/ios-arm64/libgodot.a",
    )

    moltenvk_path = "/usr/local/lib/MoltenVK.xcframework"
    if os.path.exists(moltenvk_path):
        shutil.copytree(moltenvk_path, "bin/ios_xcode/MoltenVK.xcframework", dirs_exist_ok=True)
    else:
        print(f"Warning: {moltenvk_path} not found.  Skipping MoltenVK copy.")

    cwd = os.getcwd()
    os.chdir("bin/ios_xcode")
    subprocess.run(["zip", "-vr", "../ios.zip", "."], check=True)
    os.chdir(cwd)

    copyToExportDir("ios.zip", "ios.zip")


def build_csharp():
    if os.name == "nt":
        subprocess.run(
            ["bin\godot.windows.editor.x86_64.mono.exe", "--headless", "--generate-mono-glue", "modules/mono/glue"],
            check=True,
        )
        subprocess.run(
            [
                "python",
                "./modules/mono/build_scripts/build_assemblies.py",
                "--godot-output-dir",
                "./bin",
                "--godot-platform=windows",
                "--push-nupkgs-local",
                "C:/Users/MegaMiley/Documents/godot/bin/MyLocalNugetSource",
            ],
            check=True,
        )
    else:
        subprocess.run(
            [
                "bin/godot_macos_editor_mono.app/Contents/MacOS/Godot",
                "--headless",
                "--generate-mono-glue",
                "modules/mono/glue",
            ],
            check=True,
        )
        subprocess.run(
            [
                "python3",
                "./modules/mono/build_scripts/build_assemblies.py",
                "--godot-output-dir",
                "./bin",
                "--godot-platform=macos",
                "--push-nupkgs-local",
                "~/MyLocalNugetSource",
            ],
            check=True,
        )


def clean_builds():
    shutil.rmtree("bin/obj")


selections_file = "./scripts/.build_selections"
previous_selections = {}
try:
    with open(selections_file, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            previous_selections[key] = value == "True"
except FileNotFoundError:
    pass


build_options = [
    Choice("windows_editor", name="Windows Editor", enabled=previous_selections.get("windows_editor", False)),
    Choice("windows", name="Windows", enabled=previous_selections.get("windows", False)),
    Choice("macos_editor", name="macOS Editor", enabled=previous_selections.get("macos_editor", False)),
    Choice("macos", name="macOS", enabled=previous_selections.get("macos", False)),
    Choice("android", name="Android", enabled=previous_selections.get("android", False)),
    Choice("ios", name="iOS", enabled=previous_selections.get("ios", False)),
    Choice("csharp", name="C#", enabled=previous_selections.get("csharp", False)),
]


def main():
    action = inquirer.select(
        message="Select an action:",
        choices=[
            Choice("build", name="Start Builds"),
            Choice("clean", name="Clean"),
            Choice("quit", name="Quit"),
        ],
        default="build",
    ).execute()

    if action == "quit":
        print("Exiting.")
        return

    if action == "clean":
        print("Cleaning build files...")
        clean_builds()
        return

    build_selections = inquirer.checkbox(
        message="Select build options:",
        choices=build_options,
        instruction="Press Space to toggle, Enter to confirm",
        cycle=True,
    ).execute()

    for option_data in build_options:
        if isinstance(option_data, Choice):
            option_data.enabled = option_data.value in build_selections

    with open(selections_file, "w") as f:
        for option_data in build_options:
            if isinstance(option_data, Choice):
                f.write(f"{option_data.value}={option_data.enabled}\n")

    if build_selections:
        print("Starting builds...")
        for option in build_selections:
            if option == "windows_editor":
                print("Building Windows Editor...")
                build_windows_editor()
            elif option == "windows":
                print("Building Windows...")
                build_windows()
            elif option == "macos_editor":
                print("Building MacOS Editor...")
                build_macos_editor()
            elif option == "macos":
                print("Building MacOS...")
                build_macos()
            elif option == "android":
                print("Building Android...")
                build_android()
            elif option == "ios":
                print("Building iOS...")
                build_ios()
            elif option == "csharp":
                print("Building C#...")
                build_csharp()  # on Windows the macOS Editor app bundle can't be generated before the C# stuff is ready but C# can't be made before the editor has been at least partially build (it relies upon a binary inside it which does get generated but the editor build will fail. So the order is macOS Editor, C#, macOS Editor again)

    else:
        print("No build options selected.")


if __name__ == "__main__":
    main()
