#!/usr/bin/env python3
"""
Find Available TTS Voices

This script helps you find the voice index for pyttsx3 TTS engine.
Run this script to see all available voices on your system.
"""

import pyttsx3

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    print("="*50)
    print("🎤 Available TTS Voices on this system")
    print("="*50)

    for i, voice in enumerate(voices):
        print(f"Index: {i}")
        print(f"  ID:   {voice.id}")
        print(f"  Name: {voice.name}")
        print(f"  Lang: {voice.languages}")
        print("-" * 20)

    print("="*50)
    print("📌 Copy the 'Index' number of your desired voice")
    print("   and paste it into 'voice_index' in config.json")
    print("="*50)

except Exception as e:
    print(f"❌ Error: Could not initialize TTS engine.")
    print(f"   Make sure you have a TTS engine installed on your OS.")
    print(f"   Error details: {e}")
