#!/usr/bin/env python3
"""
Debug the grounding calculation issue.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genesis as gs
from robot_grounding import RobotGroundingCalculator

def main():
    print("=== Debug Grounding Calculation ===\n")
    
    # Initialize Genesis
    gs.init()
    
    # Create scene without viewer for faster debugging
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        show_viewer=False,
    )
    
    # Add ground
    plane = scene.add_entity(gs.morphs.Plane())
    
    # Load robot at 1.0m height
    print("Loading robot at 1.0m height...")
    robot = scene.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf",
            pos=(0, 0, 1.0),
        ),
    )
    
    scene.build()
    
    # Get initial positions
    calc = RobotGroundingCalculator(robot, verbose=True)
    
    print("\nInitial positions:")
    base_pos = robot.get_pos()
    print(f"Base position: {base_pos}")
    
    foot_positions = calc.get_current_foot_positions()
    if foot_positions is not None:
        print(f"Foot positions: {foot_positions}")
        print(f"Foot Z values: {foot_positions[:, 2]}")
        lowest_foot_z = foot_positions[:, 2].min().item()
        print(f"Lowest foot Z: {lowest_foot_z:.4f}m")
    
    # Calculate what we think the grounding height should be
    ground_height = calc.get_grounding_height()
    print(f"\nCalculated grounding height: {ground_height:.4f}m")
    
    # The issue might be that we need to calculate the relative offset
    # between base and feet, not the absolute positions
    print("\nAnalyzing relationship:")
    if foot_positions is not None:
        base_z = base_pos[2].item() if base_pos.dim() == 1 else base_pos[0, 2].item()
        print(f"Base Z: {base_z:.4f}m")
        print(f"Foot Z range: {foot_positions[:, 2].min().item():.4f}m to {foot_positions[:, 2].max().item():.4f}m")
        foot_to_base_offset = base_z - foot_positions[:, 2].min().item()
        print(f"Base to lowest foot offset: {foot_to_base_offset:.4f}m")
        
        # The correct grounding height should be:
        # We want the lowest foot at 0.005m (safety margin)
        # So the base should be at 0.005 + foot_to_base_offset
        correct_height = 0.005 + foot_to_base_offset
        print(f"Correct grounding height should be: {correct_height:.4f}m")
    
    print("\nDebug complete!")

if __name__ == "__main__":
    main()