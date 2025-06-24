#!/usr/bin/env python3
"""
Improved visual demo comparing default vs automatic grounding
Shows side-by-side robot placement with and without grounding calculation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genesis as gs
import torch
from robot_grounding import RobotGroundingCalculator


def main():
    print("=== Improved Robot Grounding Comparison Demo ===")
    print("Left robot: Default height (1.0m) - will fall")
    print("Right robot: Calculated grounding + safety margin - stable")
    
    gs.init()
    
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(4.0, -2.0, 2.0),
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=40,
            res=(1280, 720),
            max_FPS=60,
        ),
        show_viewer=True,
    )
    
    scene.add_entity(gs.morphs.Plane())
    
    # Load robots with path handling
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urdf_path = os.path.join(project_root, "assets/robots/g1/g1.urdf")
    
    try:
        # Left robot at default height (for comparison)
        robot_default = scene.add_entity(
            gs.morphs.URDF(file=urdf_path, pos=(-1.5, 0, 1.0), euler=(0, 0, 0))
        )
        
        # Right robot at temporary position for calculation
        robot_grounded = scene.add_entity(
            gs.morphs.URDF(file=urdf_path, pos=(1.5, 0, 5.0), euler=(0, 0, 0))
        )
        
        scene.build()
        
        # Calculate grounding height with safety margin
        print("Calculating optimal grounding height...")
        calculator = RobotGroundingCalculator(robot_grounded, verbose=True)
        base_height = calculator.get_grounding_height()
        safety_margin = 0.03  # 3cm extra clearance
        final_height = base_height + safety_margin
        
        print(f"✓ Base height: {base_height:.4f}m")
        print(f"✓ With safety margin: {final_height:.4f}m")
        
        # Position grounded robot at calculated height
        robot_grounded.set_pos(torch.tensor([1.5, 0, final_height], device='cuda:0'))
        
        # Stabilize
        for _ in range(10):
            scene.step()
        
        # Verify placement
        calc_default = RobotGroundingCalculator(robot_default, verbose=False)
        calc_grounded = RobotGroundingCalculator(robot_grounded, verbose=False)
        
        foot_pos_grounded = calc_grounded.get_current_foot_positions()
        if foot_pos_grounded is not None:
            avg_grounded = foot_pos_grounded[:, 2].mean().item()
            min_grounded = foot_pos_grounded[:, 2].min().item()
            print(f"Grounded robot feet: {min_grounded:.4f}m to {avg_grounded:.4f}m")
            
            if avg_grounded > 0.001:
                print("✓ SUCCESS: Grounded robot feet safely above ground!")
        
        print("\nComparison Demo Running...")
        print("Expected: Left falls, Right stable with controlled descent")
        print("Controls: Mouse (rotate), Scroll (zoom), ESC (exit)")
        
        # Interactive simulation with monitoring
        step_count = 0
        try:
            while True:
                scene.step()
                step_count += 1
                
                # Status every 2 seconds
                if step_count % 200 == 0:
                    default_base = robot_default.get_pos()[2].item()
                    grounded_base = robot_grounded.get_pos()[2].item()
                    
                    default_feet = calc_default.get_current_foot_positions()
                    grounded_feet = calc_grounded.get_current_foot_positions()
                    
                    print(f"Time {step_count/100:.0f}s:")
                    if default_feet is not None:
                        avg_default = default_feet[:, 2].mean().item()
                        print(f"  Default:  Base={default_base:.3f}m, Feet={avg_default:.4f}m")
                    
                    if grounded_feet is not None:
                        avg_grounded_foot = grounded_feet[:, 2].mean().item()
                        min_grounded_foot = grounded_feet[:, 2].min().item()
                        print(f"  Grounded: Base={grounded_base:.3f}m, Feet={avg_grounded_foot:.4f}m")
                        
                        if min_grounded_foot < -0.01:
                            print("    ⚠ Foot penetration detected")
                        else:
                            print("    ✓ Robot stable")
        except KeyboardInterrupt:
            print("Comparison demo stopped by user")
    
    except Exception as e:
        print(f"✗ Failed to load G1: {e}")
        print("Demo requires G1 robot URDF in assets/robots/g1/")


if __name__ == "__main__":
    main()