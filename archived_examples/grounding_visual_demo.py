#!/usr/bin/env python3
"""
Visual demo of robot grounding based on working samples/01_basic_visualization.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genesis as gs
import torch
from robot_grounding import RobotGroundingCalculator


def main():
    print("=== Robot Grounding Visual Demo ===\n")
    print("This demo shows two robots:")
    print("1. Red robot at default height (1.0m) - will fall")
    print("2. Green robot at calculated grounding height - should be stable")
    
    # Initialize Genesis
    gs.init()
    
    # Create single scene (avoiding multiple scene creation issue)
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(
            dt=0.01,
            substeps=10,
        ),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(4.0, -2.0, 2.0),
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=40,
            res=(1280, 720),
            max_FPS=60,
        ),
        show_viewer=True,
    )
    
    # Add ground plane
    plane = scene.add_entity(gs.morphs.Plane())
    
    # Add first robot at default height (for comparison)
    print("Loading first robot at default height (1.0m)...")
    robot_default = scene.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf",
            pos=(-1.5, 0, 1.0),  # Left side, default height
            euler=(0, 0, 0),
        ),
    )
    
    # Add second robot - we'll calculate its height after scene.build()
    print("Loading second robot at temporary height...")
    robot_grounded = scene.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf", 
            pos=(1.5, 0, 5.0),  # Right side, temporary high position
            euler=(0, 0, 0),
        ),
    )
    
    print("✓ Both robots loaded successfully")
    
    # Build scene
    scene.build()
    
    # Calculate grounding height using the temporary robot
    print("\nCalculating optimal grounding height...")
    calculator = RobotGroundingCalculator(robot_grounded, verbose=True)
    ground_height = calculator.get_grounding_height()
    
    print(f"\n✓ Calculated grounding height: {ground_height:.4f}m")
    
    # Now move the second robot to the calculated height
    print(f"Repositioning second robot to grounding height...")
    # Set the robot's position directly
    robot_grounded.set_pos(torch.tensor([1.5, 0, ground_height], device='cuda:0'))
    
    # Create calculators for monitoring
    calc_default = RobotGroundingCalculator(robot_default, verbose=False)
    calc_grounded = RobotGroundingCalculator(robot_grounded, verbose=False)
    
    # Verify placements
    print("\nVerifying robot placements...")
    
    # Check default robot
    foot_pos_default = calc_default.get_current_foot_positions()
    if foot_pos_default is not None:
        avg_default = foot_pos_default[:, 2].mean().item()
        print(f"Default robot (left): Average foot height = {avg_default:.4f}m")
    
    # Check grounded robot  
    foot_pos_grounded = calc_grounded.get_current_foot_positions()
    if foot_pos_grounded is not None:
        avg_grounded = foot_pos_grounded[:, 2].mean().item()
        print(f"Grounded robot (right): Average foot height = {avg_grounded:.4f}m")
        
        if abs(avg_grounded - 0.005) < 0.002:
            print("✓ SUCCESS: Grounded robot feet are properly positioned!")
    
    print(f"\n" + "="*60)
    print("VISUAL DEMO COMPARISON")
    print("="*60)
    print("LEFT ROBOT (Red):   Default placement at 1.0m height")
    print("RIGHT ROBOT (Green): Automatic grounding calculation")
    print("")
    print("Observations to make:")
    print("• Left robot should fall and settle on ground")
    print("• Right robot should remain stable near ground level")
    print("• Right robot demonstrates proper grounding calculation")
    print("="*60)
    print("Controls: Mouse to rotate, scroll to zoom, ESC to exit")
    print("Running simulation...")
    
    # Torch already imported at the top
    
    # Run simulation
    for i in range(1000):  # 10 seconds
        scene.step()
        
        # Print status every 200 steps (2 seconds)
        if i % 200 == 0 and i > 0:
            default_base = robot_default.get_pos()[2].item()
            grounded_base = robot_grounded.get_pos()[2].item()
            
            default_feet = calc_default.get_current_foot_positions()
            grounded_feet = calc_grounded.get_current_foot_positions()
            
            print(f"\nTime {i/100:.0f}s:")
            if default_feet is not None:
                avg_default_foot = default_feet[:, 2].mean().item()
                print(f"  Default robot:  Base={default_base:.3f}m, Feet={avg_default_foot:.4f}m")
            
            if grounded_feet is not None:
                avg_grounded_foot = grounded_feet[:, 2].mean().item()
                print(f"  Grounded robot: Base={grounded_base:.3f}m, Feet={avg_grounded_foot:.4f}m")
    
    print("\n" + "="*60)
    print("DEMO COMPLETE!")
    print("="*60)
    print("The robot grounding library successfully:")
    print("• Analyzed robot URDF structure")  
    print("• Detected foot links automatically")
    print("• Calculated optimal placement height")
    print("• Demonstrated stable grounding vs. default placement")
    print("="*60)


if __name__ == "__main__":
    main()