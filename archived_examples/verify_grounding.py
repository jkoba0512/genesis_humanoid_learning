#!/usr/bin/env python3
"""
Verification script for robot grounding calculator.
This script loads a robot at the calculated height and verifies proper grounding.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genesis as gs
import torch
import time
from robot_grounding import RobotGroundingCalculator


def verify_grounding(robot, calculator, tolerance=0.01):
    """
    Verify that the robot is properly grounded.
    
    Args:
        robot: Genesis robot entity
        calculator: RobotGroundingCalculator instance
        tolerance: Acceptable distance from ground in meters
        
    Returns:
        dict: Verification results
    """
    results = {
        'is_grounded': False,
        'foot_heights': [],
        'min_height': None,
        'max_height': None,
        'average_height': None,
        'base_height': None,
        'warnings': []
    }
    
    # Get current foot positions
    foot_positions = calculator.get_current_foot_positions()
    if foot_positions is None:
        results['warnings'].append("No foot positions detected")
        return results
    
    # Extract Z coordinates (heights)
    foot_heights = foot_positions[:, 2].cpu().numpy()
    results['foot_heights'] = foot_heights.tolist()
    results['min_height'] = float(foot_heights.min())
    results['max_height'] = float(foot_heights.max())
    results['average_height'] = float(foot_heights.mean())
    
    # Get base height
    base_pos = robot.get_pos()
    if base_pos.dim() > 1:
        results['base_height'] = float(base_pos[0, 2].item())
    else:
        results['base_height'] = float(base_pos[2].item())
    
    # Check if properly grounded
    if results['min_height'] < tolerance and results['max_height'] < tolerance * 2:
        results['is_grounded'] = True
    else:
        results['warnings'].append(f"Feet not properly grounded: min={results['min_height']:.4f}m, max={results['max_height']:.4f}m")
    
    # Check for negative heights (penetration)
    if results['min_height'] < -tolerance:
        results['warnings'].append(f"Foot penetration detected: {results['min_height']:.4f}m below ground")
    
    return results


def main():
    print("=== Robot Grounding Verification ===\n")
    
    # Initialize Genesis
    gs.init()
    
    # Test Case 1: Load robot at calculated height
    print("Test Case 1: Direct placement at calculated height")
    print("-" * 50)
    
    # Create scene
    scene1 = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(3.0, -3.0, 2.0),
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=40,
            res=(1280, 720),
            max_FPS=60,
        ),
        show_viewer=True,
    )
    
    # Add ground
    plane1 = scene1.add_entity(gs.morphs.Plane())
    
    # First, load robot at temporary height to calculate grounding
    print("Loading robot at temporary height...")
    temp_robot = scene1.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf",
            pos=(0, 0, 10.0),  # High temporary position
        ),
    )
    
    scene1.build()
    
    # Calculate grounding height
    temp_calc = RobotGroundingCalculator(temp_robot, verbose=False)
    ground_height = temp_calc.get_grounding_height()
    print(f"Calculated grounding height: {ground_height:.3f}m")
    
    # Clear scene and reload at correct height
    del scene1
    
    # Create new scene with robot at calculated height
    print("\nLoading robot at calculated height...")
    scene2 = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(3.0, -3.0, 2.0),
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=40,
            res=(1280, 720),
            max_FPS=60,
        ),
        show_viewer=True,
    )
    
    plane2 = scene2.add_entity(gs.morphs.Plane())
    
    # Load robot at calculated height
    robot = scene2.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf",
            pos=(0, 0, ground_height),  # Use calculated height
        ),
    )
    
    scene2.build()
    
    # Create calculator for verification
    calculator = RobotGroundingCalculator(robot, verbose=False)
    
    print("\nLetting robot settle...")
    # Let robot settle for a moment
    for i in range(50):
        scene2.step()
    
    # Verify grounding
    print("\nVerifying robot grounding...")
    results = verify_grounding(robot, calculator)
    
    # Print results
    print("\n=== Verification Results ===")
    print(f"Robot properly grounded: {'✓ YES' if results['is_grounded'] else '✗ NO'}")
    print(f"Base height: {results['base_height']:.3f}m")
    print(f"Foot heights: {[f'{h:.4f}m' for h in results['foot_heights']]}")
    print(f"Min foot height: {results['min_height']:.4f}m")
    print(f"Max foot height: {results['max_height']:.4f}m")
    print(f"Average foot height: {results['average_height']:.4f}m")
    
    if results['warnings']:
        print("\nWarnings:")
        for warning in results['warnings']:
            print(f"  - {warning}")
    
    # Continue simulation to observe stability
    print("\nRunning simulation to check stability...")
    print("Watch the robot - it should remain stable on the ground")
    print("Press ESC to exit\n")
    
    stable_count = 0
    unstable_count = 0
    
    for i in range(300):  # 3 seconds
        scene2.step()
        
        # Check stability every 10 steps
        if i % 10 == 0:
            current_results = verify_grounding(robot, calculator, tolerance=0.02)
            if current_results['is_grounded']:
                stable_count += 1
            else:
                unstable_count += 1
            
            # Print status every second
            if i % 100 == 0:
                print(f"Time: {i/100:.1f}s - Base height: {current_results['base_height']:.3f}m, "
                      f"Foot avg: {current_results['average_height']:.4f}m")
    
    print(f"\nStability check: {stable_count} stable / {stable_count + unstable_count} total checks")
    
    if stable_count > unstable_count * 2:
        print("✓ Robot remained stable throughout the test!")
    else:
        print("✗ Robot showed instability during the test")
    
    print("\nVerification complete!")


if __name__ == "__main__":
    main()