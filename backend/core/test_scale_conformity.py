#!/usr/bin/env python3
"""
Test scale conformity calculation
Demonstrates the new distribution-based scale conformity metric
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from audio_features import calculate_scale_coverage

def test_scale_conformity():
    """Test various note distribution scenarios"""
    
    print("\n" + "="*70)
    print("Scale Conformity Distribution Test")
    print("="*70)
    
    # Define a pentatonic scale (5 notes)
    # Pitch classes: A=0, C=2, D=5, E=7, G=10
    scale_notes = {0, 2, 5, 7, 10}
    
    # Test 1: Playing only one note repeatedly
    print("\n1. Playing only ONE note (A) 100 times:")
    note_counts = {0: 100}
    score = calculate_scale_coverage(note_counts, scale_notes)
    print(f"   Note distribution: {note_counts}")
    print(f"   ❌ Scale Conformity: {score*100:.1f}% (BAD - need to use more notes!)")
    
    # Test 2: Playing two notes unevenly
    print("\n2. Playing TWO notes unevenly (A: 80 times, C: 20 times):")
    note_counts = {0: 80, 2: 20}
    score = calculate_scale_coverage(note_counts, scale_notes)
    print(f"   Note distribution: {note_counts}")
    print(f"   ⚠️  Scale Conformity: {score*100:.1f}% (UNEVEN)")
    
    # Test 3: Playing three notes somewhat evenly
    print("\n3. Playing THREE notes (A: 40, C: 35, D: 25):")
    note_counts = {0: 40, 2: 35, 5: 25}
    score = calculate_scale_coverage(note_counts, scale_notes)
    print(f"   Note distribution: {note_counts}")
    print(f"   🟡 Scale Conformity: {score*100:.1f}% (OKAY)")
    
    # Test 4: Playing all five notes perfectly evenly
    print("\n4. Playing ALL 5 notes perfectly evenly (20 each):")
    note_counts = {0: 20, 2: 20, 5: 20, 7: 20, 10: 20}
    score = calculate_scale_coverage(note_counts, scale_notes)
    print(f"   Note distribution: {note_counts}")
    print(f"   ✅ Scale Conformity: {score*100:.1f}% (PERFECT!)")
    
    # Test 5: Playing all five notes in real scenario
    print("\n5. Playing all 5 notes more realistically (A:50, C:45, D:40, E:35, G:30):")
    note_counts = {0: 50, 2: 45, 5: 40, 7: 35, 10: 30}
    score = calculate_scale_coverage(note_counts, scale_notes)
    total = sum(note_counts.values())
    print(f"   Note distribution: {note_counts}")
    print(f"   Percentages: A={50/total*100:.1f}%, C={45/total*100:.1f}%, D={40/total*100:.1f}%, E={35/total*100:.1f}%, G={30/total*100:.1f}%")
    print(f"   🟢 Scale Conformity: {score*100:.1f}% (GOOD)")
    
    # Test 6: Progressive improvement
    print("\n6. Progressive Improvement Over Time:")
    scenarios = [
        ("Start: playing A 100x", {0: 100}),
        ("Add C: A 100, C 50", {0: 100, 2: 50}),
        ("Add D: A 100, C 50, D 40", {0: 100, 2: 50, 5: 40}),
        ("Add E: A 100, C 50, D 40, E 35", {0: 100, 2: 50, 5: 40, 7: 35}),
        ("Add G: A 100, C 50, D 40, E 35, G 30", {0: 100, 2: 50, 5: 40, 7: 35, 10: 30}),
    ]
    
    for label, counts in scenarios:
        score = calculate_scale_coverage(counts, scale_notes)
        print(f"   {label}")
        print(f"     → Scale Conformity: {score*100:.1f}%")
    
    # Test 7: Playing bad notes (notes not in the scale)
    print("\n7. Playing with BAD NOTES (should lower distribution score):")
    print("   a) All 5 scale notes evenly (20 each) - PERFECT:")
    note_counts = {0: 20, 2: 20, 5: 20, 7: 20, 10: 20}
    score = calculate_scale_coverage(note_counts, scale_notes)
    print(f"      Note distribution: {note_counts}")
    print(f"      ✅ Scale Conformity: {score*100:.1f}% (PERFECT!)")
    
    print("   b) All 5 scale notes evenly (20 each) + 20 bad notes (pitch class 1):")
    note_counts = {0: 20, 1: 20, 2: 20, 5: 20, 7: 20, 10: 20}  # pitch class 1 not in scale
    score = calculate_scale_coverage(note_counts, scale_notes)
    print(f"      Note distribution: {note_counts}")
    print(f"      ❌ Scale Conformity: {score*100:.1f}% (Should be LOWER due to bad notes!)")
    
    print("   c) All 5 scale notes evenly (20 each) + 100 bad notes:")
    note_counts = {0: 20, 1: 50, 2: 20, 4: 50, 5: 20, 7: 20, 10: 20}  # pitch classes 1,4 not in scale
    score = calculate_scale_coverage(note_counts, scale_notes)
    print(f"      Note distribution: {note_counts}")
    print(f"      ❌ Scale Conformity: {score*100:.1f}% (Should be MUCH LOWER!)")

    print("\n" + "="*70)
    print("Key Insight:")
    print("  • Solo note: ~20% (1/5 notes)")
    print("  • Two notes:  ~50% of perfectly even")
    print("  • Three notes: ~75% of perfectly even")
    print("  • All notes evenly: 100%")
    print("  • Bad notes (not in scale): Should LOWER the score!")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_scale_conformity()
