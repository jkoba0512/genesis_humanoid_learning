#!/usr/bin/env python3
"""
Simple visual demonstration of automatic robot grounding
Shows robot placement using automatic height calculation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import genesis as gs
import torch
from robot_grounding import RobotGroundingCalculator


def main():
    print("=== Simple Robot Grounding Visual Demo ===")
    
    gs.init()
    
    # Create scene with viewer
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(3.0, -1.0, 1.5),
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=40,
            res=(1280, 720),
            max_FPS=60,
        ),
        show_viewer=True,
    )
    
    scene.add_entity(gs.morphs.Plane())
    
    # Load robot with automatic grounding
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urdf_path = os.path.join(project_root, "assets/robots/g1/g1.urdf")
    
    try:
        robot = scene.add_entity(
            gs.morphs.URDF(file=urdf_path, pos=(0, 0, 1.0), euler=(0, 0, 0))
        )
        scene.build()
        
        print("Calculating optimal grounding height...")
        calculator = RobotGroundingCalculator(robot, verbose=True)
        grounding_height = calculator.get_grounding_height(safety_margin=0.03)
        
        # Apply grounding
        robot.set_pos(torch.tensor([0, 0, grounding_height], device='cuda:0'))
        print(f"✓ Robot positioned at grounding height: {grounding_height:.4f}m")
        
        # Stabilize
        for _ in range(10):
            scene.step()
        
        # Verify placement
        foot_positions = calculator.get_current_foot_positions()
        if foot_positions is not None:
            avg_height = foot_positions[:, 2].mean().item()
            min_height = foot_positions[:, 2].min().item()
            max_height = foot_positions[:, 2].max().item()
            print(f"Foot heights: {min_height:.4f}m to {max_height:.4f}m (avg: {avg_height:.4f}m)")
            
            if abs(avg_height - 0.005) < 0.002:
                print("✓ SUCCESS: Robot feet properly positioned on ground!")
        
        print("\nVisual Demo Running...")
        print("Controls: Mouse (rotate), Scroll (zoom), ESC (exit)")
        print("="*50)
        
        # Interactive simulation
        try:
            while True:
                scene.step()
        except KeyboardInterrupt:
            print("Demo stopped by user")
        
    except Exception as e:
        print(f"✗ Failed to load G1: {e}")
        print("Demo requires G1 robot URDF in assets/robots/g1/")


if __name__ == "__main__":
    main()