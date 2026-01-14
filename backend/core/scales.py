"""
Musical scales and pitch class definitions.
Contains all major and minor keys with their pitch classes.
"""

# Pitch class numbers: C=0, C#=1, D=2, D#=3, E=4, F=5, F#=6, G=7, G#=8, A=9, A#=10, B=11

MAJOR_SCALES = {
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

MINOR_SCALES = {
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

ALL_SCALES = {**MAJOR_SCALES, **MINOR_SCALES}


def get_scale_choices():
    """Return a list of all available scale names."""
    return sorted(ALL_SCALES.keys())


def get_pitch_classes(scale_name):
    """Get pitch classes for a given scale name."""
    return ALL_SCALES.get(scale_name)


def select_scale_interactive():
    """
    Interactive scale selection.
    Returns tuple of (scale_name, pitch_classes).
    """
    print("\n" + "="*60)
    print("SELECT MUSICAL SCALE")
    print("="*60)
    
    # Display major scales
    print("\nMAJOR SCALES:")
    major_scales = sorted([s for s in ALL_SCALES.keys() if "Major" in s])
    for i, scale in enumerate(major_scales, 1):
        print(f"  {i:2d}. {scale}")
    
    # Display minor scales
    print("\nMINOR SCALES:")
    minor_scales = sorted([s for s in ALL_SCALES.keys() if "Minor" in s])
    for i, scale in enumerate(minor_scales, len(major_scales) + 1):
        print(f"  {i:2d}. {scale}")
    
    print("="*60)
    
    # Combine scales in the same order as displayed
    all_scales_ordered = major_scales + minor_scales
    
    while True:
        try:
            choice = input("\nEnter scale number: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(all_scales_ordered):
                selected_scale = all_scales_ordered[idx]
                pitch_classes = ALL_SCALES[selected_scale]
                print(f"✓ Selected: {selected_scale}")
                print(f"  Pitch classes: {sorted(pitch_classes)}")
                return selected_scale, pitch_classes
            else:
                print(f"Please enter a number between 1 and {len(all_scales_ordered)}")
        except ValueError:
            print("Invalid input. Please enter a number.")


if __name__ == "__main__":
    # Test the module
    scale_name, pitch_classes = select_scale_interactive()
    print(f"\nYou selected: {scale_name}")
    print(f"Pitch classes: {pitch_classes}")
