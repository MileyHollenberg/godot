#!/bin/bash

if [[ $(pwd) != */godot ]]; then
  echo "This script must be ran from the godot root directory via ./scripts/build.sh"
  exit 0
fi

# Extract variables from versions.py
MAJOR=$(grep "major =" version.py | awk '{print $3}')
MINOR=$(grep "minor =" version.py | awk '{print $3}')
PATCH=$(grep "patch =" version.py | awk '{print $3}')
STATUS=$(grep "status =" version.py | awk '{print $3}' | tr -d '"') # Remove quotes

# Construct the version string
if [ "$PATCH" -eq "0" ]; then
  GODOT_VERSION="$MAJOR.$MINOR.$STATUS.mono"
else
  GODOT_VERSION="$MAJOR.$MINOR.$PATCH.$STATUS.mono"
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  export SCRIPT_AES256_ENCRYPTION_KEY=$(cat /Users/MegaMiley/Documents/AndroidKeystore/godot.gdkey)
elif [[ "$OSTYPE" == "msys"* ]]; then
  # Windows (Git Bash, etc.)
  export SCRIPT_AES256_ENCRYPTION_KEY=$(cat /e/AndroidKeystore/godot.gdkey)
else
  # Some other OS, handle appropriately or error
  echo "Unsupported OS detected, can't retrieve the godot.gdkey"
  exit 1
fi

source /e/emsdk/emsdk_env.sh

# Define build options and their corresponding functions/scripts
declare -A build_options=(
  ["windows_editor"]="build_windows_editor"
  ["windows"]="build_windows"
  ["macos_editor"]="build_macos_editor"
  ["macos"]="build_macos"
  ["web"]="build_web"
  ["android"]="build_android"
  ["ios"]="build_ios"
  ["csharp"]="build_csharp"
)

# Function to execute a build script
build_windows() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
	echo "Refusing to build Windows binaries on macOS"
    return
  fi
  
  cp ./bin/godot.windows.template_debug.x86_32.mono.console.exe "$APPDATA/Godot/export_templates/$GODOT_VERSION/windows_debug_x86_32_console.exe"
  cp ./bin/godot.windows.template_debug.x86_32.mono.exe "$APPDATA/Godot/export_templates/$GODOT_VERSION/windows_debug_x86_32.exe"
  cp ./bin/godot.windows.template_release.x86_32.mono.console.exe "$APPDATA/Godot/export_templates/$GODOT_VERSION/windows_release_x86_32_console.exe"
  cp ./bin/godot.windows.template_release.x86_32.mono.exe "$APPDATA/Godot/export_templates/$GODOT_VERSION/windows_release_x86_32.exe"
  
  cp ./bin/godot.windows.template_debug.x86_64.mono.console.exe "$APPDATA/Godot/export_templates/$GODOT_VERSION/windows_debug_x86_64_console.exe"
  cp ./bin/godot.windows.template_debug.x86_64.mono.exe "$APPDATA/Godot/export_templates/$GODOT_VERSION/windows_debug_x86_64.exe"
  cp ./bin/godot.windows.template_release.x86_64.mono.console.exe "$APPDATA/Godot/export_templates/$GODOT_VERSION/windows_release_x86_64_console.exe"
  cp ./bin/godot.windows.template_release.x86_64.mono.exe "$APPDATA/Godot/export_templates/$GODOT_VERSION/windows_release_x86_64.exe"
}

build_windows_editor() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
	echo "Refusing to build Windows binaries on macOS"
    return
  fi
  
  ./scripts/compile_windows_editor.sh
}

build_macos() {
  if [[ "$OSTYPE" == "msys"* ]]; then
    # macOS
	echo "Refusing to build macOS binaries on Windows"
    return
  fi
  
  ./scripts/compile_macos.sh
}

build_macos_editor() {
  if [[ "$OSTYPE" == "msys"* ]]; then
    # macOS
	echo "Refusing to build macOS binaries on Windows"
    return
  fi
  
  ./scripts/compile_macos_editor.sh
}

build_web() {
  ./scripts/compile_web.sh
  
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "todo"
  elif [[ "$OSTYPE" == "msys"* ]]; then
    # Windows (Git Bash, etc.)
    cp ./bin/godot.web.template_debug.wasm32.zip "$APPDATA/Godot/export_templates/$GODOT_VERSION/web_debug.zip"
    cp ./bin/godot.web.template_release.wasm32.zip "$APPDATA/Godot/export_templates/$GODOT_VERSION/web_release.zip"
  fi
}

build_android() {
  ./scripts/compile_android.sh
  
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "todo"
  elif [[ "$OSTYPE" == "msys"* ]]; then
    # Windows (Git Bash, etc.)
    cp ./bin/android_source.zip "$APPDATA/Godot/export_templates/$GODOT_VERSION/android_source.zip"
    cp ./bin/android_monoDebug.apk "$APPDATA/Godot/export_templates/$GODOT_VERSION/android_debug.apk"
    cp ./bin/android_monoRelease.apk "$APPDATA/Godot/export_templates/$GODOT_VERSION/android_release.apk"
  fi
}

build_ios() {
  if [[ "$OSTYPE" == "msys"* ]]; then
    # macOS
	echo "Refusing to build macOS binaries on Windows"
    return
  fi
  
  ./scripts/compile_ios.sh
  # TODO
}

build_csharp() {
  ./scripts/compile_csharp.sh
}

clean_builds() {
  ./scripts/clean.sh ./bin
}

# Load previous selections (if any) - Simple text file storage
selections_file="./scripts/.build_selections" # Or a more appropriate location
if [ -f "$selections_file" ]; then
  source "$selections_file"
fi

# Initialize selections if not loaded
if [ -z "$selected_windows_editor" ]; then
  selected_windows_editor="false"
fi
if [ -z "$selected_windows" ]; then
  selected_windows="false"
fi
if [ -z "$selected_macos_editor" ]; then
  selected_macos_editor="false"
fi
if [ -z "$selected_macos" ]; then
  selected_macos="false"
fi
if [ -z "$selected_web" ]; then
  selected_web="false"
fi
if [ -z "$selected_android" ]; then
  selected_android="false"
fi
if [ -z "$selected_ios" ]; then
  selected_ios="false"
fi
if [ -z "$selected_csharp" ]; then
  selected_csharp="false"
fi

# Initialize selected index
selected_index=0
num_options=8 # Number of build options

# Function to display the menu and get user input
show_menu() {
  clear
  echo "Build Options:"

  local windows_editor_marker="   "
  local windows_marker="   "
  local macos_editor_marker="   "
  local macos_marker="   "
  local web_marker="   "
  local android_marker="   "
  local ios_marker="   "
  local csharp_marker="   "

  if [ "$selected_index" -eq 0 ]; then
    windows_editor_marker=" ->"
  fi
  if [ "$selected_index" -eq 1 ]; then
    windows_marker=" ->"
  fi
  if [ "$selected_index" -eq 2 ]; then
    macos_editor_marker=" ->"
  fi
  if [ "$selected_index" -eq 3 ]; then
    macos_marker=" ->"
  fi
  if [ "$selected_index" -eq 4 ]; then
    web_marker=" ->"
  fi
  if [ "$selected_index" -eq 5 ]; then
    android_marker=" ->"
  fi
  if [ "$selected_index" -eq 6 ]; then
    ios_marker=" ->"
  fi
  if [ "$selected_index" -eq 7 ]; then
    csharp_marker=" ->"
  fi


  echo "$windows_editor_marker [$([ "$selected_windows_editor" = "true" ] && echo "X" || echo " ")] Windows Editor"
  echo "$windows_marker [$([ "$selected_windows" = "true" ] && echo "X" || echo " ")] Windows"
  echo "$macos_editor_marker [$([ "$selected_macos_editor" = "true" ] && echo "X" || echo " ")] MacOS Editor"
  echo "$macos_marker [$([ "$selected_macos" = "true" ] && echo "X" || echo " ")] MacOS"
  echo "$web_marker [$([ "$selected_web" = "true" ] && echo "X" || echo " ")] Web (No C# available yet)"
  echo "$android_marker [$([ "$selected_android" = "true" ] && echo "X" || echo " ")] Android"
  echo "$ios_marker [$([ "$selected_ios" = "true" ] && echo "X" || echo " ")] iOS"
  echo "$csharp_marker [$([ "$selected_csharp" = "true" ] && echo "X" || echo " ")] C#"
  echo "[S] Start Builds"
  echo "[C] Clean"
  echo "[Q] Quit"

  # Use stty to read single characters with timeout
  old_tty_settings=$(stty -g)
  stty raw -echo -icanon time 0 min 0 # time is timeout in deciseconds, min is minimum chars

  read -r -n 3 -t 0.5 input # Read up to 3 characters, timeout after 0.1 seconds

  stty "$old_tty_settings" # Restore original terminal settings

  case "$input" in
    $'\e[A') # Up arrow
      selected_index=$(( (selected_index - 1 + num_options) % num_options ))
      show_menu
      ;;
    $'\e[B') # Down arrow
      selected_index=$(( (selected_index + 1) % num_options ))
      show_menu
      ;;
    $'\e[C'|$'\e[D'|" "|"\r")  # Right/Left arrow, Space, Enter
      case "$selected_index" in
        0)
          selected_windows_editor=$([ "$selected_windows_editor" = "true" ] && echo "false" || echo "true")
          ;;
        1)
          selected_windows=$([ "$selected_windows" = "true" ] && echo "false" || echo "true")
          ;;
        2)
          selected_macos_editor=$([ "$selected_macos_editor" = "true" ] && echo "false" || echo "true")
          ;;
        3)
          selected_macos=$([ "$selected_macos" = "true" ] && echo "false" || echo "true")
          ;;
        4)
          selected_web=$([ "$selected_web" = "true" ] && echo "false" || echo "true")
          ;;
        5)
          selected_android=$([ "$selected_android" = "true" ] && echo "false" || echo "true")
          ;;
        6)
          selected_ios=$([ "$selected_ios" = "true" ] && echo "false" || echo "true")
          ;;
        7)
          selected_csharp=$([ "$selected_csharp" = "true" ] && echo "false" || echo "true")
          ;;
      esac
      show_menu
      ;;
    s|S)
      echo "Starting Builds..."
      run_builds
      ;;
    c|C)
      echo "Cleaning build files..."
      clean_builds
      show_menu
      ;;
    q|Q)
      echo "Exiting."
      exit 0
      ;;
    "") # Timeout (no input)
        show_menu # Redraw the menu
        ;;
    *)
      echo "Invalid choice."
      show_menu
      ;;
  esac
}

# Function to execute the selected builds
run_builds() {
  # Save selections for next time
  echo "selected_windows_editor=\"$selected_windows_editor\"" > "$selections_file"
  echo "selected_windows=\"$selected_windows\"" >> "$selections_file"
  echo "selected_macos_editor=\"$selected_macos_editor\"" >> "$selections_file"
  echo "selected_macos=\"$selected_macos\"" >> "$selections_file"
  echo "selected_web=\"$selected_web\"" >> "$selections_file"
  echo "selected_android=\"$selected_android\"" >> "$selections_file"
  echo "selected_ios=\"$selected_ios\"" >> "$selections_file"
  echo "selected_csharp=\"$selected_csharp\"" >> "$selections_file"

  if [ "$selected_windows_editor" = "true" ]; then
    echo "Building Windows Editor..."
    build_windows_editor
  fi
  if [ "$selected_windows" = "true" ]; then
    echo "Building Windows..."
    build_windows
  fi
  if [ "$selected_macos_editor" = "true" ]; then
    echo "Building MacOS Editor..."
    build_macos_editor
  fi
  if [ "$selected_macos" = "true" ]; then
    echo "Building MacOS..."
    build_macos
  fi
  if [ "$selected_web" = "true" ]; then
    echo "Building Web..."
    build_web
  fi
  if [ "$selected_android" = "true" ]; then
    echo "Building Android..."
    build_android
  fi
  if [ "$selected_ios" = "true" ]; then
    echo "Building iOS..."
    build_ios
  fi
  if [ "$selected_csharp" = "true" ]; then
    echo "Building C#..."
    build_csharp
  fi
}

# Start the menu
show_menu