import os
import subprocess
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from InquirerPy.base.control import Choice
import platform

# Check if the script is being run from the correct directory
if os.path.basename(os.getcwd()) != "godot":
    print("This script must be run from the godot root directory via ./scripts/build.py")
    exit(1)

# Extract variables from versions.py
try:
    with open("version.py", "r") as f:
        version_content = f.read()
        MAJOR = eval(
            next(line.split("=")[1].strip() for line in version_content.splitlines() if "major =" in line)
        )
        MINOR = eval(
            next(line.split("=")[1].strip() for line in version_content.splitlines() if "minor =" in line)
        )
        PATCH = eval(
            next(line.split("=")[1].strip() for line in version_content.splitlines() if "patch =" in line)
        )
        STATUS = next(
            line.split("=")[1].strip().strip('"') for line in version_content.splitlines() if "status =" in line
        )
except (FileNotFoundError, StopIteration) as e:
    print(f"Error reading version.py: {e}")
    exit(1)

# Construct the version string
if PATCH == 0:
    GODOT_VERSION = f"{MAJOR}.{MINOR}.{STATUS}.mono"
else:
    GODOT_VERSION = f"{MAJOR}.{MINOR}.{PATCH}.{STATUS}.mono"

# Determine the operating system
# if os.name == "posix":  # macOS and Linux
#     if os.uname().sysname == "Darwin":  # macOS
#         try:
#             with open(os.path.expanduser("~/Documents/AndroidKeystore/godot.gdkey"), "r") as f:
#                 os.environ["SCRIPT_AES256_ENCRYPTION_KEY"] = f.read().strip()
#         except FileNotFoundError:
#             print("Error: godot.gdkey not found at ~/Documents/AndroidKeystore/")
#             exit(1)
#     else:
#         print("Unsupported OS detected, can't retrieve the godot.gdkey")
#         exit(1)
#
# elif os.name == "nt":  # Windows
#     try:
#         with open(os.path.join("E:", "AndroidKeystore", "godot.gdkey"), "r") as f:
#             os.environ["SCRIPT_AES256_ENCRYPTION_KEY"] = f.read().strip()
#     except FileNotFoundError:
#         print("Error: godot.gdkey not found at E:\\AndroidKeystore\\")
#         exit(1)
# else:
#     print("Unsupported OS detected.")
#     exit(1)


def copyToExportDir(sourceFile, targetName):
    if os.name == "posix" and platform.system() == "Darwin":
        home_dir = os.path.expanduser("~")
        template_dir = os.path.join(home_dir, "Library", "Application Support", "Godot", "export_templates", GODOT_VERSION)
        try:
            os.makedirs(template_dir, exist_ok=True)
            subprocess.run(
                [
                    "cp",
                    "./bin/" + sourceFile,
                    os.path.join(template_dir, targetName),
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error copying files: {e}")
        except OSError as e:
            print(f"Error creating directories: {e}")
    elif os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            appdata = os.path.expanduser("~/.config")  # Fallback for Git Bash
        try:
            os.makedirs(os.path.join(appdata, "Godot", "export_templates", GODOT_VERSION), exist_ok=True)
            subprocess.run(
                [
                    "cp",
                    "./bin/" + sourceFile,
                    os.path.join(appdata, "Godot", "export_templates", GODOT_VERSION, targetName),
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error copying files: {e}")
        except OSError as e:
            print(f"Error creating directories: {e}")

# Define build options and their corresponding functions/scripts
def build_windows():
    if os.name == "posix" and os.uname().sysname == "Darwin":
        print("Refusing to build Windows binaries on macOS")
        return
    subprocess.run(["./scripts/compile_windows.sh"], shell=True, check=True)
    
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
    subprocess.run(["./scripts/compile_windows_editor.sh"], shell=True, check=True)


def build_macos():
    if os.name == "nt":
        print("Refusing to build macOS binaries on Windows")
        return
    subprocess.run(["./scripts/compile_macos.sh"], shell=True, check=True)
    copyToExportDir("godot_macos_mono.zip", "macos.zip")


def build_macos_editor():
    if os.name == "nt":
        print("Refusing to build macOS binaries on Windows")
        return
    subprocess.run(["./scripts/compile_macos_editor.sh"], shell=True, check=True)


def build_web():
    subprocess.run(["./scripts/compile_web.sh"], shell=True, check=True)
    
    copyToExportDir("godot.web.template_debug.wasm32.zip", "web_debug.zip")
    copyToExportDir("godot.web.template_release.wasm32.zip", "web_release.zip")


def build_android():
    subprocess.run(["./scripts/compile_android.sh"], shell=True, check=True)
    
    copyToExportDir("android_source.zip", "android_source.zip")
    copyToExportDir("android_monoDebug.apk", "android_debug.apk")
    copyToExportDir("android_monoRelease.apk", "android_release.apk")


def build_ios():
    if os.name == "nt":
        print("Refusing to build iOS binaries on Windows")
        return
    subprocess.run(["./scripts/compile_ios.sh"], shell=True, check=True)
    
    copyToExportDir("ios.zip", "ios.zip")


def build_csharp():
    if os.name == "nt":
        subprocess.run(["./scripts/compile_csharp_windows.sh"], shell=True, check=True)
    else:
        subprocess.run(["./scripts/compile_csharp_macos.sh"], shell=True, check=True)


def clean_builds():
    subprocess.run(["./scripts/clean.sh", "./bin"], shell=True, check=True)


# Load previous selections (if any)
selections_file = "./scripts/.build_selections"
previous_selections = {}
try:
    with open(selections_file, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            previous_selections[key] = value == "True"
except FileNotFoundError:
    pass


# Define build options for the interactive menu
build_options = [
    Choice("windows_editor", name="Windows Editor", enabled=previous_selections.get("windows_editor", False)),
    Choice("windows", name="Windows", enabled=previous_selections.get("windows", False)),
    Choice("macos_editor", name="macOS Editor", enabled=previous_selections.get("macos_editor", False)),
    Choice("macos", name="macOS", enabled=previous_selections.get("macos", False)),
    Choice("web", name="Web (No C# available yet)", enabled=previous_selections.get("web", False)),
    Choice("android", name="Android", enabled=previous_selections.get("android", False)),
    Choice("ios", name="iOS", enabled=previous_selections.get("ios", False)),
    Choice("csharp", name="C#", enabled=previous_selections.get("csharp", False)),
]


# Interactive menu using InquirerPy
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
        cycle=False,
    ).execute()

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
            elif option == "web":
                print("Building Web...")
                build_web()
            elif option == "android":
                print("Building Android...")
                build_android()
            elif option == "ios":
                print("Building iOS...")
                build_ios()
            elif option == "csharp":
                print("Building C#...")
                build_csharp()

    else:
        print("No build options selected.")

    # Update previous selections for persistence
    for option_data in build_options:
        if isinstance(option_data, Choice):
            option_data.enabled = option_data.value in build_selections

    # Save selections to file
    with open(selections_file, "w") as f:
        for option_data in build_options:
            if isinstance(option_data, Choice):
                f.write(f"{option_data.value}={option_data.enabled}\n")


if __name__ == "__main__":
    main()
