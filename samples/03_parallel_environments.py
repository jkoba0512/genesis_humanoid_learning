#!/usr/bin/env python3
"""
Genesis sample: Parallel environments for RL training
This sample demonstrates:
- Multiple parallel simulation environments
- Batch robot control with different motion patterns
- Performance optimization and data collection
"""

import genesis as gs
import numpy as np
import torch
import time
import os
import sys

# Import robot grounding library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from robot_grounding import RobotGroundingCalculator


def main():
    gs.init()
    
    n_envs = 4
    print(f"Creating {n_envs} parallel environments...")
    
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01, substeps=10),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(5.0, -3.0, 3.0),
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=50,
            res=(1280, 720),
            max_FPS=60,
        ),
        show_viewer=True,
    )
    
    scene.add_entity(gs.morphs.Plane())
    
    # Add camera for recording parallel environments
    camera = scene.add_camera(
        res=(1280, 720),
        pos=(6.0, -4.0, 4.0),
        lookat=(1.5, 1.5, 1.0),  # Center of robot grid
        fov=60,  # Wide angle to capture all robots
        GUI=False
    )
    
    # Load robots with automatic grounding
    robots = []
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urdf_path = os.path.join(project_root, "assets/robots/g1/g1.urdf")
    
    try:
        for i in range(n_envs):
            robot = scene.add_entity(
                gs.morphs.URDF(
                    file=urdf_path,
                    pos=(i % 2 * 3.0, i // 2 * 3.0, 1.0),
                    euler=(0, 0, 0),
                )
            )
            robots.append(robot)
        
        scene.build()
        
        # Apply automatic grounding to all robots
        print("Calculating grounding heights for all robots...")
        for i, robot in enumerate(robots):
            calculator = RobotGroundingCalculator(robot, verbose=False)
            grounding_height = calculator.get_grounding_height(safety_margin=0.03)
            
            x_pos = i % 2 * 3.0
            y_pos = i // 2 * 3.0
            robot.set_pos(torch.tensor([x_pos, y_pos, grounding_height], device='cuda:0'))
            print(f"  Robot {i}: positioned at ({x_pos:.1f}, {y_pos:.1f}, {grounding_height:.3f})")
        
        # Stabilize robots
        for _ in range(10):
            scene.step()
            
        print("✓ All G1 robots loaded and grounded successfully")
        
    except Exception as e:
        print(f"✗ Failed to load G1 robots: {e}")
        for i in range(n_envs):
            robot = scene.add_entity(
                gs.morphs.Box(size=(0.3, 0.2, 1.8), pos=(i % 2 * 3.0, i // 2 * 3.0, 0.9))
            )
            robots.append(robot)
        scene.build()
        print("✓ Using fallback box models")
    
    print(f"\n=== Genesis Parallel Environments Sample ===")
    print(f"Running {n_envs} parallel environments")
    print(f"Robot DOF count: {robots[0].n_dofs}")
    
    # Initialize control arrays
    n_dofs = robots[0].n_dofs
    all_initial_pos = np.zeros((n_envs, n_dofs))
    
    for i, robot in enumerate(robots):
        all_initial_pos[i] = robot.get_dofs_position().cpu().numpy()
    
    # Simulation parameters
    step_count = 0
    max_steps = 300
    start_time = time.time()
    
    # Start recording
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    video_path = f"samples/videos/03_parallel_environments_{timestamp}.mp4"
    
    os.makedirs("samples/videos", exist_ok=True)
    camera.start_recording()
    print("Recording parallel environments demo...")
    
    print("\nStarting parallel simulation with different motion patterns...")
    
    try:
        while step_count < max_steps:
            t = step_count * 0.01
            
            # Display simulation time in console every second
            if step_count % 100 == 0:
                print(f"Parallel simulation ({n_envs} robots) - Time: {t:.1f}s/3.0s")
            
            # Automatically end at 3 seconds
            if t >= 3.0:
                break
            
            for i, robot in enumerate(robots):
                phase_offset = (i / n_envs) * 2 * np.pi
                frequency = 1.0 + 0.1 * i
                
                target_pos = all_initial_pos[i].copy()
                
                # Different motion patterns per robot
                if n_dofs > 6:
                    if i % 4 == 0:
                        # Pattern 1: Simple oscillation
                        amplitude = 0.3
                        target_pos[0] += amplitude * np.sin(2 * np.pi * frequency * t + phase_offset)
                        target_pos[1] += amplitude * np.cos(2 * np.pi * frequency * t + phase_offset)
                    
                    elif i % 4 == 1:
                        # Pattern 2: Walking-like motion
                        step_amp = 0.4
                        target_pos[0] += step_amp * np.sin(2 * np.pi * frequency * t + phase_offset)
                        if n_dofs > 6:
                            target_pos[6] += step_amp * np.sin(2 * np.pi * frequency * t + phase_offset + np.pi)
                    
                    elif i % 4 == 2:
                        # Pattern 3: Multi-joint motion
                        for j in range(min(4, n_dofs)):
                            joint_phase = phase_offset + j * np.pi / 2
                            target_pos[j] += 0.2 * np.sin(2 * np.pi * frequency * t + joint_phase)
                    
                    else:
                        # Pattern 4: Static with perturbations
                        perturbation = 0.1 * np.sin(2 * np.pi * 0.5 * t + phase_offset)
                        target_pos += perturbation
                
                try:
                    robot.control_dofs_position(torch.tensor(target_pos, device='cuda'))
                except Exception as e:
                    print(f"Control error for robot {i}: {e}")
            
            scene.step()
            
            # Render frame for recording
            camera.render(rgb=True)
            
            # Performance stats
            if step_count % 100 == 0 and step_count > 0:
                elapsed_time = time.time() - start_time
                total_env_steps = step_count * n_envs
                env_steps_per_sec = total_env_steps / elapsed_time
                
                print(f"Step {step_count}/{max_steps}")
                print(f"  Environment steps/sec: {env_steps_per_sec:.0f}")
                
                # Sample robot data
                for i in [0, n_envs//2, n_envs-1]:
                    pos = robots[i].get_dofs_position().cpu().numpy()
                    vel = robots[i].get_dofs_velocity().cpu().numpy()
                    print(f"  Robot {i}: pos[0]={pos[0]:.3f}, vel[0]={vel[0]:.3f}")
            
            step_count += 1
        
        # Stop recording and save
        camera.stop_recording(save_to_filename=video_path, fps=60)
        print(f"\n✓ Video saved: {video_path}")
        print(f"Parallel simulation completed at {step_count * 0.01:.1f} seconds")
        
    except KeyboardInterrupt:
        camera.stop_recording(save_to_filename=video_path, fps=60)
        print(f"\n✓ Video saved: {video_path}")
        print(f"Parallel simulation stopped by user at {step_count * 0.01:.1f} seconds")
    
    # Performance summary
    total_time = time.time() - start_time
    total_env_steps = max_steps * n_envs
    
    print(f"\n=== Performance Summary ===")
    print(f"Total simulation time: {total_time:.2f} seconds")
    print(f"Environment steps: {total_env_steps}")
    print(f"Environment steps/sec: {total_env_steps / total_time:.0f}")
    print(f"Performance per environment: {total_env_steps / total_time / n_envs:.1f} steps/sec")
    
    print("\nParallel simulation completed!")


if __name__ == "__main__":
    main()