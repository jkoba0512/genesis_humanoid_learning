#!/usr/bin/env python3
"""
Example of using robot grounding calculator to place robot with feet on ground.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genesis as gs
from robot_grounding import RobotGroundingCalculator


def main():
    print("=== Robot Grounding Example ===\n")
    print("Demonstrating automatic robot placement with feet on ground")
    
    # Initialize Genesis
    gs.init()
    
    # Step 1: Calculate grounding height using temporary robot
    print("\nStep 1: Calculating optimal grounding height...")
    
    temp_scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        show_viewer=False,  # No viewer for calculation phase
    )
    
    temp_plane = temp_scene.add_entity(gs.morphs.Plane())
    temp_robot = temp_scene.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf",
            pos=(0, 0, 10.0),  # Temporary high position for calculation
        ),
    )
    
    temp_scene.build()
    
    # Calculate grounding height
    temp_calculator = RobotGroundingCalculator(temp_robot, verbose=True)
    ground_height = temp_calculator.get_grounding_height()
    
    print(f"\n✓ Calculated grounding height: {ground_height:.4f}m")
    print(f"  This places the robot base at {ground_height:.4f}m above ground")
    print(f"  With feet positioned 5mm above ground for stable contact")
    
    # Clean up temporary scene
    del temp_scene
    
    # Step 2: Create final scene with robot at calculated height
    print(f"\nStep 2: Creating scene with robot at calculated height ({ground_height:.4f}m)...")
    
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(
            dt=0.01,
            substeps=10,
        ),
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
    plane = scene.add_entity(gs.morphs.Plane())
    
    # Load robot at calculated grounding height
    print(f"Loading robot at grounding height: {ground_height:.4f}m")
    robot = scene.add_entity(
        gs.morphs.URDF(
            file="assets/robots/g1/g1.urdf",
            pos=(0, 0, ground_height),  # Use calculated height
        ),
    )
    
    # Build scene
    scene.build()
    
    # Create calculator for monitoring
    calculator = RobotGroundingCalculator(robot, verbose=False)
    
    # Verify initial placement
    print("\nStep 3: Verifying initial placement...")
    initial_foot_positions = calculator.get_current_foot_positions()
    if initial_foot_positions is not None:
        foot_heights = initial_foot_positions[:, 2]
        print(f"Initial foot heights: {foot_heights.min().item():.4f}m to {foot_heights.max().item():.4f}m")
        print(f"Average foot height: {foot_heights.mean().item():.4f}m")
        
        if abs(foot_heights.mean().item() - 0.005) < 0.002:
            print("✓ SUCCESS: Robot feet are properly positioned near ground!")
        else:
            print("⚠ Warning: Robot feet may not be optimally positioned")
    
    # Run simulation to show stability
    print("\nStep 4: Running simulation to demonstrate stability...")
    print("The robot should remain stable with feet on ground")
    print("Press ESC to exit\n")
    
    for i in range(300):  # 3 seconds
        scene.step()
        
        # Monitor robot status every second
        if i % 100 == 0:
            current_base = robot.get_pos()[2].item()
            current_feet = calculator.get_current_foot_positions()
            
            if current_feet is not None:
                avg_foot_height = current_feet[:, 2].mean().item()
                print(f"Time {i/100:.1f}s: Base={current_base:.3f}m, Avg foot height={avg_foot_height:.4f}m")
            else:
                print(f"Time {i/100:.1f}s: Base={current_base:.3f}m")
    
    print("\n=== Summary ===")
    print(f"Robot was automatically placed at height {ground_height:.4f}m")
    print("This ensures feet are positioned for stable ground contact")
    print("The robot grounding library successfully calculated the optimal placement!")
    print("\nDemo completed!")


if __name__ == "__main__":
    main()