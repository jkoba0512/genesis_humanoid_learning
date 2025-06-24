#!/usr/bin/env python3
"""
Quick test of 30mm safety margin for robot grounding
Tests optimal safety margin to prevent ground penetration and jumping
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genesis as gs
import torch
from robot_grounding import RobotGroundingCalculator


def main():
    print("=== Quick Test: 30mm Safety Margin ===")
    
    gs.init()
    
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(3.0, -2.0, 1.5),
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=40,
            res=(1024, 576),
            max_FPS=30,
        ),
        show_viewer=True,
    )
    
    scene.add_entity(gs.morphs.Plane())
    
    # Load robot with path handling
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urdf_path = os.path.join(project_root, "assets/robots/g1/g1.urdf")
    
    try:
        robot = scene.add_entity(
            gs.morphs.URDF(file=urdf_path, pos=(0, 0, 5.0), euler=(0, 0, 0))
        )
        scene.build()
        
        # Calculate grounding with 30mm safety margin
        print("Calculating grounding height...")
        calculator = RobotGroundingCalculator(robot, verbose=False)
        base_height = calculator.get_grounding_height()
        
        safety_margin = 0.03  # 30mm
        final_height = base_height + safety_margin
        
        print(f"Base calculated height: {base_height:.4f}m")
        print(f"30mm safety margin: +{safety_margin*1000:.0f}mm")
        print(f"Final placement height: {final_height:.4f}m")
        
        # Position robot
        robot.set_pos(torch.tensor([0, 0, final_height], device='cuda:0'))
        
        # Stabilize
        for _ in range(20):
            scene.step()
        
        # Check initial placement
        foot_positions = calculator.get_current_foot_positions()
        if foot_positions is not None:
            avg_height = foot_positions[:, 2].mean().item()
            min_height = foot_positions[:, 2].min().item()
            
            print(f"\nInitial foot placement:")
            print(f"Average foot height: {avg_height:.4f}m")
            print(f"Minimum foot height: {min_height:.4f}m")
            
            if min_height > 0.02:
                print("✓ EXCELLENT: Large clearance, no jumping expected")
            elif min_height > 0.01:
                print("✓ GOOD: Adequate clearance")
            elif min_height > 0.005:
                print("✓ ACCEPTABLE: Minimal clearance")
            else:
                print("⚠ WARNING: May still cause jumping")
        
        print("\nRunning simulation (3 seconds)...")
        print("Watch for jumping behavior!")
        
        # Simulation with monitoring
        for i in range(300):
            scene.step()
            
            if i % 100 == 0 and i > 0:
                current_base = robot.get_pos()[2].item()
                current_feet = calculator.get_current_foot_positions()
                
                if current_feet is not None:
                    avg_foot = current_feet[:, 2].mean().item()
                    min_foot = current_feet[:, 2].min().item()
                    
                    print(f"Time {i/100:.0f}s: Base={current_base:.3f}m, Feet avg={avg_foot:.4f}m, min={min_foot:.4f}m")
                    
                    if current_base > final_height + 0.05:
                        print("  ⚠ JUMPING DETECTED!")
                    elif abs(current_base - final_height) < 0.02:
                        print("  ✓ Stable positioning")
                    else:
                        print("  → Natural settling")
        
        print("\n=== Test Complete ===")
        print("30mm safety margin test finished!")
        
    except Exception as e:
        print(f"✗ Failed to load G1: {e}")
        print("Test requires G1 robot URDF in assets/robots/g1/")


if __name__ == "__main__":
    main()