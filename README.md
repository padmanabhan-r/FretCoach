# FretCoach - An Adaptive Guitar Learning Agent

![FretCoach](images/FretCoach.jpeg)

> *"FretCoach is like an AI guitar pedal that trains your brain, not your tone."*

## Overview

FretCoach is an edge-first AI learning agent designed to function like an intelligent guitar pedal for beginners, helping players fine-tune their playing through real-time evaluation and adaptive visual feedback. Instead of effects like distortion or delay, FretCoach provides **learning effects**.

## How It Works

FretCoach listens to live guitar input and evaluates:
- **Pitch accuracy**
- **Scale conformity**
- **Timing stability**
- **Note transitions**

It translates performance quality into immediate visual lighting cues. These cues act as a subconscious training signal, allowing the brain to adapt and self-correct while playing — much like how traditional pedals shape tone.

## Intelligent Coaching

Beyond real-time feedback, FretCoach operates as an autonomous coach. The system:
- Aggregates performance metrics over time
- Identifies dominant learning bottlenecks
- Uses a large language model in a slow, reflective loop to synthesize structured metrics
- Diagnoses learning issues and adapts future training strategies

All real-time audio analysis and feedback remain **deterministic** and run locally on a Raspberry Pi.

## Key Features

- **Real-time visual feedback** - Instant lighting cues guide your playing
- **Edge-first architecture** - Runs entirely on Raspberry Pi
- **Adaptive learning** - AI analyzes patterns and adjusts training
- **Embodied feedback** - Physical, tangible learning experience
- **Extensible design** - Architecture can generalize to other instruments and vocal training

## Philosophy

FretCoach transforms unstructured practice into a guided learning loop, acting as a physical, intelligent pedal that trains the player — not the sound. While demonstrated for guitar practice, the architecture is designed to generalize to other instruments and vocal training that benefit from adaptive, embodied feedback.
