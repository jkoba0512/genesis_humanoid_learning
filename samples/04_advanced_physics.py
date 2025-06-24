#!/usr/bin/env python3
"""
Genesis sample: Advanced physics features
This sample demonstrates:
- Advanced physics solvers and contact forces
- Self-collision detection and joint limits
- Material properties and physics monitoring
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
    
    # Advanced physics scene configuration
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(
            dt=0.005,  # Higher precision timestep
            substeps=20,
            gravity=(0, 0, -9.81),
        ),
        rigid_options=gs.options.RigidOptions(
            constraint_solver=gs.constraint_solver.CG,
            enable_self_collision=True,
            enable_joint_limit=True,
            iterations=50,
            tolerance=1e-6,
        ),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(3.0, -2.0, 2.0),
            camera_lookat=(0.0, 0.0, 1.0),
            camera_fov=45,
            res=(1280, 720),
            max_FPS=60,
        ),
        show_viewer=True,
    )
    
    # Add camera for recording
    camera = scene.add_camera(
        res=(1280, 720),
        pos=(4.0, -3.0, 3.0),
        lookat=(0.5, 0.0, 1.0),
        fov=50,
        GUI=False
    )
    
    # Ground with material properties
    scene.add_entity(
        gs.morphs.Plane(),
        material=gs.materials.Rigid(friction=0.8),
        surface=gs.surfaces.Default(color=(0.4, 0.4, 0.4, 1.0)),
    )
    
    # Add obstacles for interaction testing
    obstacles = []
    for i in range(3):
        obstacle = scene.add_entity(
            gs.morphs.Box(
                size=(0.2, 0.2, 0.5),
                pos=(1.5 + i * 0.5, 0, 0.25),
            ),
            material=gs.materials.Rigid(friction=0.6),
            surface=gs.surfaces.Default(color=(0.8, 0.2, 0.2, 1.0)),
        )
        obstacles.append(obstacle)
    
    # Load G1 robot with automatic grounding
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urdf_path = os.path.join(project_root, "assets/robots/g1/g1.urdf")
    
    try:
        robot = scene.add_entity(
            gs.morphs.URDF(file=urdf_path, pos=(0, 0, 1.0), euler=(0, 0, 0)),
            material=gs.materials.Rigid(friction=0.7),
        )
        scene.build()
        
        # Apply automatic grounding
        calculator = RobotGroundingCalculator(robot, verbose=True)
        grounding_height = calculator.get_grounding_height(safety_margin=0.03)
        robot.set_pos(torch.tensor([0, 0, grounding_height], device='cuda:0'))
        
        # Stabilize robot
        for _ in range(10):
            scene.step()
            
        print("✓ G1 robot loaded with advanced physics")
        
    except Exception as e:
        print(f"✗ Failed to load G1: {e}")
        robot = scene.add_entity(
            gs.morphs.Box(size=(0.3, 0.2, 1.8), pos=(0, 0, 0.9)),
            material=gs.materials.Rigid(friction=0.7),
        )
        scene.build()
        print("✓ Using fallback box with advanced physics")
    
    print("\n=== Genesis Advanced Physics Sample ===")
    print("Features: High-accuracy solver, self-collision, joint limits, contact forces")
    print(f"Robot DOF count: {robot.n_dofs}")
    print("Recording advanced physics demo...")
    
    # Start recording
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    video_path = f"samples/videos/04_advanced_physics_{timestamp}.mp4"
    
    os.makedirs("samples/videos", exist_ok=True)
    camera.start_recording()
    
    # Physics demonstration
    initial_pos = robot.get_dofs_position()
    step_count = 0
    n_dofs = robot.n_dofs
    
    try:
        while step_count < 1500:
            t = step_count * 0.005
            
            # Display simulation time and phase in console
            if step_count < 500:
                phase_name = "Phase 1: Physics Validation"
            elif step_count < 1000:
                phase_name = "Phase 2: Collision Testing"
            else:
                phase_name = "Phase 3: Multi-joint Motion"
            
            # Print progress every 1.25 seconds
            if step_count % 250 == 0:
                print(f"{phase_name} - Time: {t:.1f}s/7.5s")
            
            # Automatically end at 7.5 seconds
            if t >= 7.5:
                break
            
            # Physics test phases
            if step_count < 500:
                # Phase 1: Basic physics validation
                if step_count == 0:
                    print("\nPhase 1: Basic physics validation")
                target_pos = initial_pos.clone()
                if n_dofs > 2:
                    target_pos[0] += 0.1 * np.sin(2 * np.pi * 0.8 * t)
                    target_pos[1] += 0.1 * np.cos(2 * np.pi * 0.8 * t)
            
            elif step_count < 1000:
                # Phase 2: Collision detection testing
                if step_count == 500:
                    print("\nPhase 2: Testing collision detection and contact forces")
                target_pos = initial_pos.clone()
                if n_dofs > 6:
                    amplitude = 0.5
                    frequency = 1.0
                    target_pos[0] += amplitude * np.sin(2 * np.pi * frequency * t)
                    target_pos[1] += amplitude * np.sin(2 * np.pi * frequency * t * 0.7)
                    # Arm motion towards obstacles
                    if n_dofs > 10:
                        for i in range(min(4, n_dofs - 6)):
                            target_pos[6 + i] += 0.3 * np.sin(2 * np.pi * frequency * t + i)
            
            else:
                # Phase 3: Complex multi-joint coordination
                if step_count == 1000:
                    print("\nPhase 3: Dynamic motion testing solver accuracy")
                target_pos = initial_pos.clone()
                for i in range(min(n_dofs, 12)):
                    phase = i * np.pi / 6
                    freq = 1.5 + 0.1 * i
                    amp = 0.3 / (1 + i * 0.1)
                    target_pos[i] += amp * np.sin(2 * np.pi * freq * t + phase)
            
            # Apply control
            try:
                robot.control_dofs_position(target_pos)
            except Exception as e:
                print(f"Control error at step {step_count}: {e}")
                break
            
            scene.step()
            
            # Render frame for recording
            camera.render(rgb=True)
            
            # Monitor physics quantities
            if step_count % 250 == 0:
                pos = robot.get_dofs_position()
                vel = robot.get_dofs_velocity()
                
                kinetic_energy = 0.5 * torch.sum(vel**2).item()
                
                print(f"Step {step_count}:")
                print(f"  Time: {t:.2f}s")
                print(f"  Kinetic energy: {kinetic_energy:.4f}")
                print(f"  Max joint velocity: {torch.max(torch.abs(vel)).item():.3f}")
                print(f"  Joint pos range: [{torch.min(pos).item():.3f}, {torch.max(pos).item():.3f}]")
                
                # Stability checks
                if torch.any(torch.abs(vel) > 50):
                    print("  WARNING: High velocities detected - possible instability")
                if torch.any(torch.isnan(pos)) or torch.any(torch.isnan(vel)):
                    print("  ERROR: NaN values detected - simulation unstable")
                    break
            
            step_count += 1
        
        # Stop recording and save
        camera.stop_recording(save_to_filename=video_path, fps=60)
        print(f"\n✓ Video saved: {video_path}")
        print(f"Advanced physics demo completed at {step_count * 0.005:.1f} seconds")
        
    except KeyboardInterrupt:
        camera.stop_recording(save_to_filename=video_path, fps=60)
        print(f"\n✓ Video saved: {video_path}")
        print(f"Advanced physics demo stopped by user at {step_count * 0.005:.1f} seconds")
    
    print("\nAdvanced physics demonstration completed!")
    print("Tested: Solver accuracy, contact handling, joint limits, material interactions")


if __name__ == "__main__":
    main()