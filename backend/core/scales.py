"""
Musical scales and pitch class definitions.
Contains all major and minor keys with their pitch classes.
"""

# Pitch class numbers: C=0, C#=1, D=2, D#=3, E=4, F=5, F#=6, G=7, G#=8, A=9, A#=10, B=11

# Diatonic scales (7 notes)
MAJOR_DIATONIC = {
    "C Major": {0, 2, 4, 5, 7, 9, 11},
    "C# Major": {1, 3, 5, 6, 8, 10, 0},
    "D Major": {2, 4, 6, 7, 9, 11, 1},
    "D# Major": {3, 5, 7, 8, 10, 0, 2},
    "E Major": {4, 6, 8, 9, 11, 1, 3},
    "F Major": {5, 7, 9, 10, 0, 2, 4},
    "F# Major": {6, 8, 10, 11, 1, 3, 5},
    "G Major": {7, 9, 11, 0, 2, 4, 6},
    "G# Major": {8, 10, 0, 1, 3, 5, 7},
    "A Major": {9, 11, 1, 2, 4, 6, 8},
    "A# Major": {10, 0, 2, 3, 5, 7, 9},
    "B Major": {11, 1, 3, 4, 6, 8, 10},
}

MINOR_DIATONIC = {
    "C Minor": {0, 2, 3, 5, 7, 8, 10},
    "C# Minor": {1, 3, 4, 6, 8, 9, 11},
    "D Minor": {2, 4, 5, 7, 9, 10, 0},
    "D# Minor": {3, 5, 6, 8, 10, 11, 1},
    "E Minor": {4, 6, 7, 9, 11, 0, 2},
    "F Minor": {5, 7, 8, 10, 0, 1, 3},
    "F# Minor": {6, 8, 9, 11, 1, 2, 4},
    "G Minor": {7, 9, 10, 0, 2, 3, 5},
    "G# Minor": {8, 10, 11, 1, 3, 4, 6},
    "A Minor": {9, 11, 0, 2, 4, 5, 7},
    "A# Minor": {10, 0, 1, 3, 5, 6, 8},
    "B Minor": {11, 1, 2, 4, 6, 7, 9},
}

# Pentatonic scales (5 notes)
MAJOR_PENTATONIC = {
    "C Major": {0, 2, 4, 7, 9},
    "C# Major": {1, 3, 5, 8, 10},
    "D Major": {2, 4, 6, 9, 11},
    "D# Major": {3, 5, 7, 10, 0},
    "E Major": {4, 6, 8, 11, 1},
    "F Major": {5, 7, 9, 0, 2},
    "F# Major": {6, 8, 10, 1, 3},
    "G Major": {7, 9, 11, 2, 4},
    "G# Major": {8, 10, 0, 3, 5},
    "A Major": {9, 11, 1, 4, 6},
    "A# Major": {10, 0, 2, 5, 7},
    "B Major": {11, 1, 3, 6, 8},
}

MINOR_PENTATONIC = {
    "C Minor": {0, 3, 5, 7, 10},
    "C# Minor": {1, 4, 6, 8, 11},
    "D Minor": {2, 5, 7, 9, 0},
    "D# Minor": {3, 6, 8, 10, 1},
    "E Minor": {4, 7, 9, 11, 2},
    "F Minor": {5, 8, 10, 0, 3},
    "F# Minor": {6, 9, 11, 1, 4},
    "G Minor": {7, 10, 0, 2, 5},
    "G# Minor": {8, 11, 1, 3, 6},
    "A Minor": {9, 0, 2, 4, 7},
    "A# Minor": {10, 1, 3, 5, 8},
    "B Minor": {11, 2, 4, 6, 9},
}

# Legacy compatibility - keep old names
MAJOR_SCALES = MAJOR_DIATONIC
MINOR_SCALES = MINOR_DIATONIC
ALL_SCALES = {**MAJOR_DIATONIC, **MINOR_DIATONIC}


def get_scale_choices():
    """Return a list of all available scale names."""
    return sorted(ALL_SCALES.keys())


def get_pitch_classes(scale_name):
    """Get pitch classes for a given scale name."""
    return ALL_SCALES.get(scale_name)


def select_scale_interactive():
    """
    Interactive scale selection with two-step process:
    1. Select the scale (key and mode)
    2. Choose diatonic or pentatonic
    
    Returns tuple of (scale_name, pitch_classes).
    """
    print("\n" + "="*60)
    print("SELECT MUSICAL SCALE")
    print("="*60)
    
    # Step 1: Display scale choices (without diatonic/pentatonic distinction)
    print("\nMAJOR SCALES:")
    major_scales = sorted(MAJOR_DIATONIC.keys())
    for i, scale in enumerate(major_scales, 1):
        print(f"  {i:2d}. {scale}")
    
    print("\nMINOR SCALES:")
    minor_scales = sorted(MINOR_DIATONIC.keys())
    for i, scale in enumerate(minor_scales, len(major_scales) + 1):
        print(f"  {i:2d}. {scale}")
    
    print("="*60)
    
    # Combine scales in the same order as displayed
    all_scales_ordered = major_scales + minor_scales
    
    # Get scale selection
    selected_scale = None
    while True:
        try:
            choice = input("\nEnter scale number: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(all_scales_ordered):
                selected_scale = all_scales_ordered[idx]
                print(f"✓ Selected: {selected_scale}")
                break
            else:
                print(f"Please enter a number between 1 and {len(all_scales_ordered)}")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Step 2: Choose diatonic or pentatonic
    print("\n" + "="*60)
    print("SELECT SCALE TYPE")
    print("="*60)
    print("\n  1. Diatonic (7 notes) - Complete scale")
    print("  2. Pentatonic (5 notes) - Simplified scale for blues/rock")
    print("="*60)
    
    scale_type = None
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == "1":
            scale_type = "diatonic"
            break
        elif choice == "2":
            scale_type = "pentatonic"
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    # Get the appropriate pitch classes
    is_major = "Major" in selected_scale
    
    if scale_type == "diatonic":
        pitch_classes = MAJOR_DIATONIC[selected_scale] if is_major else MINOR_DIATONIC[selected_scale]
        full_name = f"{selected_scale} (Diatonic)"
    else:
        pitch_classes = MAJOR_PENTATONIC[selected_scale] if is_major else MINOR_PENTATONIC[selected_scale]
        full_name = f"{selected_scale} (Pentatonic)"
    
    print(f"\n✓ Final selection: {full_name}")
    print(f"  Pitch classes: {sorted(pitch_classes)}")
    print(f"  Number of notes: {len(pitch_classes)}")
    
    return full_name, pitch_classes


if __name__ == "__main__":
    # Test the module
    scale_name, pitch_classes = select_scale_interactive()
    print(f"\nYou selected: {scale_name}")
    print(f"Pitch classes: {pitch_classes}")
