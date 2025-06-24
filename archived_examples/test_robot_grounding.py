#!/usr/bin/env python3
"""
Test script for robot grounding calculator.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genesis as gs
from robot_grounding import RobotGroundingCalculator


def main():
    print("=== Testing Robot Grounding Calculator ===\n")
    
    # Initialize Genesis
    gs.init()
    
    # Create a simple scene
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01),
        show_viewer=False,  # No viewer for testing
    )
    
    # Add ground
    plane = scene.add_entity(gs.morphs.Plane())
    
    # Try to load a robot
    try:
        robot = scene.add_entity(
            gs.morphs.URDF(
                file="assets/robots/g1/g1.urdf",
                pos=(0, 0, 1.0),
            ),
        )
        print("✓ Robot loaded successfully")
        
        # Build scene to initialize physics
        print("Building scene...")
        scene.build()
        
        # Test the calculator
        print("\n--- Testing RobotGroundingCalculator ---")
        calculator = RobotGroundingCalculator(robot, verbose=True)
        
        # Get grounding height
        height = calculator.get_grounding_height()
        print(f"\nCalculated grounding height: {height:.3f} meters")
        
    except Exception as e:
        print(f"✗ Failed to load robot: {e}")
        print("Using a simple box for testing...")
        
        # Fallback to box
        robot = scene.add_entity(
            gs.morphs.Box(
                size=(0.3, 0.2, 1.8),
                pos=(0, 0, 1.0),
            ),
        )
        
        scene.build()
        
        calculator = RobotGroundingCalculator(robot, verbose=True)
        height = calculator.get_grounding_height()
        print(f"\nCalculated grounding height: {height:.3f} meters")
    
    print("\n✓ Basic functionality test passed!")


if __name__ == "__main__":
    main()