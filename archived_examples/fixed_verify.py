#!/usr/bin/env python3
"""
Fixed verification of robot grounding.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genesis as gs
from robot_grounding import RobotGroundingCalculator

def main():
    print("=== Fixed Grounding Verification ===\n")
    
    # Initialize Genesis
    gs.init()
    
    # Step 1: Calculate the grounding height
    print("Step 1: Calculate grounding height from temporary position")
    scene1 = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        show_viewer=False,
    )
    
    plane1 = scene1.add_entity(gs.morphs.Plane())
    temp_robot = scene1.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf",
            pos=(0, 0, 1.0),
        ),
    )
    
    scene1.build()
    
    calc1 = RobotGroundingCalculator(temp_robot, verbose=False)
    ground_height = calc1.get_grounding_height()
    print(f"Calculated grounding height: {ground_height:.4f}m")
    
    # Clean up
    del scene1
    
    # Step 2: Load robot at calculated height and verify
    print(f"\nStep 2: Load robot at calculated height ({ground_height:.4f}m)")
    scene2 = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        show_viewer=False,
    )
    
    plane2 = scene2.add_entity(gs.morphs.Plane())
    robot = scene2.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf",
            pos=(0, 0, ground_height),  # Use calculated height
        ),
    )
    
    scene2.build()
    
    calc2 = RobotGroundingCalculator(robot, verbose=False)
    
    # Check initial positions
    print("Initial positions after loading at calculated height:")
    base_pos = robot.get_pos()
    base_z = base_pos[2].item() if base_pos.dim() == 1 else base_pos[0, 2].item()
    print(f"  Base Z: {base_z:.4f}m")
    
    foot_positions = calc2.get_current_foot_positions()
    if foot_positions is not None:
        foot_z_values = foot_positions[:, 2]
        print(f"  Foot Z range: {foot_z_values.min().item():.4f}m to {foot_z_values.max().item():.4f}m")
        lowest_foot = foot_z_values.min().item()
        print(f"  Lowest foot: {lowest_foot:.4f}m")
        
        # Check if properly grounded (should be ~5mm above ground)
        expected_height = 0.005  # 5mm safety margin
        error = abs(lowest_foot - expected_height)
        
        if error < 0.002:  # Within 2mm tolerance
            print(f"  ✓ SUCCESS: Robot properly grounded (error: {error*1000:.1f}mm)")
        else:
            print(f"  ✗ FAILED: Robot not properly grounded (error: {error*1000:.1f}mm)")
    
    # Let robot settle and check again
    print("\nLetting robot settle for 1 second...")
    for i in range(100):
        scene2.step()
    
    print("After settling:")
    base_pos_final = robot.get_pos()
    base_z_final = base_pos_final[2].item() if base_pos_final.dim() == 1 else base_pos_final[0, 2].item()
    print(f"  Base Z: {base_z_final:.4f}m")
    
    foot_positions_final = calc2.get_current_foot_positions()
    if foot_positions_final is not None:
        foot_z_final = foot_positions_final[:, 2]
        print(f"  Foot Z range: {foot_z_final.min().item():.4f}m to {foot_z_final.max().item():.4f}m")
        lowest_foot_final = foot_z_final.min().item()
        print(f"  Lowest foot: {lowest_foot_final:.4f}m")
        
        # Check final grounding (should be very close to 0)
        if abs(lowest_foot_final) < 0.01:  # Within 1cm of ground
            print(f"  ✓ SUCCESS: Robot settled properly on ground")
        else:
            print(f"  ⚠  NOTICE: Robot settled {lowest_foot_final*1000:.1f}mm from ground")
    
    print("\nVerification complete!")

if __name__ == "__main__":
    main()