#!/usr/bin/env python3
"""
Genesis sample: Basic robot control with Unitree G1
This sample demonstrates:
- Joint position control and reading robot state
- Basic motion patterns (oscillation, walking-like)
- DOF manipulation with automatic grounding
"""

import genesis as gs
import numpy as np
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
        pos=(3.5, -2.0, 2.0),
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
    
    print("\n=== Genesis Robot Control Sample ===")
    print(f"Robot DOF count: {robot.n_dofs}")
    print(f"Robot link count: {robot.n_links}")
    
    # Get initial pose
    initial_pos = robot.get_dofs_position()
    print(f"Initial joint positions: {initial_pos[:8]}...")
    
    # Start recording
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    video_path = f"samples/videos/02_robot_control_{timestamp}.mp4"
    
    os.makedirs("samples/videos", exist_ok=True)
    camera.start_recording()
    print("Recording robot control demo...")
    
    step_count = 0
    
    try:
        while step_count < 2000:
            # Display simulation time and phase in console
            sim_time = step_count * 0.01
            
            if step_count < 300:
                phase_name = "Phase 1: Hold"
            elif step_count < 800:
                phase_name = "Phase 2: Oscillation"
            elif step_count < 1500:
                phase_name = "Phase 3: Walking"
            else:
                phase_name = "Phase 4: Return"
            
            # Print progress every 2 seconds
            if step_count % 200 == 0:
                print(f"{phase_name} - Time: {sim_time:.1f}s/20.0s")
            
            # Automatically end at 20 seconds
            if sim_time >= 20.0:
                break
            # Control patterns
            if step_count < 300:
                # Phase 1: Hold initial pose
                if step_count == 0:
                    print("\nPhase 1: Holding initial pose")
                target_pos = initial_pos.clone()
            
            elif step_count < 800:
                # Phase 2: Joint oscillation
                if step_count == 300:
                    print("\nPhase 2: Joint oscillation")
                t = (step_count - 300) * 0.01
                target_pos = initial_pos.clone()
                
                if robot.n_dofs > 6:
                    amplitude = 0.3
                    frequency = 0.8
                    target_pos[0] += amplitude * np.sin(2 * np.pi * frequency * t)
                    target_pos[1] += amplitude * np.cos(2 * np.pi * frequency * t)
                    if robot.n_dofs > 8:
                        target_pos[6] += amplitude * np.sin(2 * np.pi * frequency * t + np.pi)
                        target_pos[7] += amplitude * np.cos(2 * np.pi * frequency * t + np.pi)
            
            elif step_count < 1500:
                # Phase 3: Walking-like motion
                if step_count == 800:
                    print("\nPhase 3: Walking-like motion pattern")
                t = (step_count - 800) * 0.01
                target_pos = initial_pos.clone()
                
                if robot.n_dofs > 12:
                    walking_freq = 1.2
                    step_amplitude = 0.4
                    
                    # Left leg
                    target_pos[0] += step_amplitude * np.sin(2 * np.pi * walking_freq * t)
                    target_pos[1] += step_amplitude * np.sin(2 * np.pi * walking_freq * t + np.pi/2)
                    
                    # Right leg (opposite phase)
                    if robot.n_dofs > 6:
                        target_pos[6] += step_amplitude * np.sin(2 * np.pi * walking_freq * t + np.pi)
                        target_pos[7] += step_amplitude * np.sin(2 * np.pi * walking_freq * t + 3*np.pi/2)
            
            else:
                # Phase 4: Return to initial pose
                if step_count == 1500:
                    print("\nPhase 4: Returning to initial pose")
                target_pos = initial_pos.clone()
            
            # Apply control
            try:
                robot.control_dofs_position(target_pos)
            except Exception as e:
                print(f"Control error: {e}")
                break
            
            scene.step()
            
            # Render frame for recording
            camera.render(rgb=True)
            
            # Print status periodically
            if step_count % 300 == 0:
                current_pos = robot.get_dofs_position()
                current_vel = robot.get_dofs_velocity()
                print(f"Step {step_count}: Pos[0]={current_pos[0]:.3f}, Vel[0]={current_vel[0]:.3f}")
            
            step_count += 1
        
        # Stop recording and save
        camera.stop_recording(save_to_filename=video_path, fps=60)
        print(f"\n✓ Video saved: {video_path}")
        print(f"Demo completed at {step_count * 0.01:.1f} seconds!")
        
    except KeyboardInterrupt:
        camera.stop_recording(save_to_filename=video_path, fps=60)
        print(f"\n✓ Video saved: {video_path}")
        print("Demo stopped by user")


if __name__ == "__main__":
    main()