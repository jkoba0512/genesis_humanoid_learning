#!/usr/bin/env python3
"""
Quick verification of robot grounding - simplified version.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genesis as gs
from robot_grounding import RobotGroundingCalculator


def main():
    print("=== Quick Grounding Verification ===\n")
    
    # Initialize Genesis
    gs.init()
    
    # Create scene without viewer for faster execution
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        show_viewer=False,  # No viewer for speed
    )
    
    # Add ground
    plane = scene.add_entity(gs.morphs.Plane())
    
    # Test 1: Load at default height (1.0m)
    print("Test 1: Robot at default height (1.0m)")
    robot1 = scene.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf",
            pos=(0, 0, 1.0),
        ),
    )
    
    scene.build()
    
    # Calculate where it should be
    calc1 = RobotGroundingCalculator(robot1, verbose=False)
    ground_height = calc1.get_grounding_height()
    
    # Let it fall and settle
    print("  Simulating fall...")
    for i in range(100):  # 1 second
        scene.step()
    
    # Check foot positions
    foot_pos1 = calc1.get_current_foot_positions()
    if foot_pos1 is not None:
        avg_foot_height1 = foot_pos1[:, 2].mean().item()
        print(f"  After fall: Average foot height = {avg_foot_height1:.4f}m")
        print(f"  Calculated grounding height was: {ground_height:.3f}m")
    
    # Clear and create new scene
    del scene
    
    # Test 2: Load at calculated height
    print("\nTest 2: Robot at calculated height")
    scene2 = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        show_viewer=False,
    )
    
    plane2 = scene2.add_entity(gs.morphs.Plane())
    
    # Use the calculated height
    robot2 = scene2.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf",
            pos=(0, 0, ground_height),
        ),
    )
    
    scene2.build()
    
    calc2 = RobotGroundingCalculator(robot2, verbose=False)
    
    # Check immediately
    foot_pos2_initial = calc2.get_current_foot_positions()
    if foot_pos2_initial is not None:
        avg_foot_height2_initial = foot_pos2_initial[:, 2].mean().item()
        print(f"  Initial: Average foot height = {avg_foot_height2_initial:.4f}m")
    
    # Let it settle
    print("  Simulating settling...")
    for i in range(100):  # 1 second
        scene2.step()
    
    # Check after settling
    foot_pos2_final = calc2.get_current_foot_positions()
    if foot_pos2_final is not None:
        avg_foot_height2_final = foot_pos2_final[:, 2].mean().item()
        min_foot_height = foot_pos2_final[:, 2].min().item()
        max_foot_height = foot_pos2_final[:, 2].max().item()
        
        print(f"  After settling: Average foot height = {avg_foot_height2_final:.4f}m")
        print(f"  Min foot height: {min_foot_height:.4f}m")
        print(f"  Max foot height: {max_foot_height:.4f}m")
        
        # Verify grounding
        tolerance = 0.02  # 2cm tolerance
        if abs(avg_foot_height2_final) < tolerance:
            print("\n✓ SUCCESS: Robot is properly grounded!")
            print(f"  Feet are within {tolerance*1000:.0f}mm of ground")
        else:
            print("\n✗ FAILED: Robot is not properly grounded")
            print(f"  Feet are {abs(avg_foot_height2_final)*1000:.1f}mm from ground")
    
    # Compare heights
    print(f"\n=== Summary ===")
    print(f"Calculated grounding height: {ground_height:.3f}m")
    print(f"This places the pelvis {ground_height:.3f}m above ground")
    print(f"With feet approximately 5mm above ground")
    
    print("\nVerification complete!")


if __name__ == "__main__":
    main()