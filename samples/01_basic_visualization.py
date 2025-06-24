#!/usr/bin/env python3
"""
Basic Genesis sample: Load and visualize Unitree G1 humanoid robot
This sample demonstrates:
- Genesis initialization and scene creation
- Loading URDF robot model with automatic grounding
- Basic visualization and interactive controls
"""

import genesis as gs
import torch
import os
import sys

# Import robot grounding library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from robot_grounding import RobotGroundingCalculator


def main():
    gs.init()
    
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
    
    # Add camera for recording
    camera = scene.add_camera(
        res=(1280, 720),
        pos=(4.0, -2.0, 2.0),
        lookat=(0.0, 0.0, 1.0),
        fov=45,
        GUI=False
    )
    
    # Load G1 robot with automatic grounding
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urdf_path = os.path.join(project_root, "assets/robots/g1/g1.urdf")
    
    try:
        robot = scene.add_entity(
            gs.morphs.URDF(file=urdf_path, pos=(0, 0, 1.0), euler=(0, 0, 0))
        )
        scene.build()
        
        # Apply automatic grounding
        calculator = RobotGroundingCalculator(robot, verbose=True)
        grounding_height = calculator.get_grounding_height(safety_margin=0.03)
        robot.set_pos(torch.tensor([0, 0, grounding_height], device='cuda:0'))
        
        # Stabilize robot
        for _ in range(10):
            scene.step()
            
        print("✓ G1 robot loaded and grounded successfully")
        
    except Exception as e:
        print(f"✗ Failed to load G1: {e}")
        robot = scene.add_entity(gs.morphs.Box(size=(0.3, 0.2, 1.8), pos=(0, 0, 0.9)))
        scene.build()
        print("✓ Using fallback box model")
    
    print("\n=== Genesis Basic Visualization ===")
    print("Controls: Mouse (rotate), Scroll (zoom), ESC (exit), Space (pause)")
    print("Recording simulation...")
    
    # Start recording
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    video_path = f"samples/videos/01_basic_visualization_{timestamp}.mp4"
    
    # Ensure videos directory exists
    os.makedirs("samples/videos", exist_ok=True)
    
    try:
        camera.start_recording()
        step_count = 0
        
        # Record for 150 steps (2.5 seconds at 60fps)
        while step_count < 150:
            # Display simulation time in console
            sim_time = step_count * 0.01
            if step_count % 30 == 0:  # Print every 0.5 seconds
                print(f"Recording... Time: {sim_time:.1f}s/{2.5:.1f}s")
            
            scene.step()
            
            # Render frame for recording
            camera.render(rgb=True)
            
            step_count += 1
        
        # Stop recording and save
        camera.stop_recording(save_to_filename=video_path, fps=60)
        print(f"✓ Video saved: {video_path}")
        print("Simulation completed at 2.5 seconds")
            
    except KeyboardInterrupt:
        camera.stop_recording(save_to_filename=video_path, fps=60)
        print(f"✓ Video saved: {video_path}")
        print("Simulation stopped by user")
    except Exception as e:
        print(f"Recording error: {e}")
        print("Simulation completed")


if __name__ == "__main__":
    main()