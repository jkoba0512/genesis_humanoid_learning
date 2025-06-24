"""
Genesis API demonstration for link positions, transforms, and forward kinematics.

This script shows how to:
1. Get link positions and orientations
2. Use forward kinematics
3. Access transformation matrices between links
4. Get specific link information
"""

import numpy as np
import genesis as gs


def main():
    # Initialize Genesis
    gs.init(backend=gs.cuda)
    
    # Create scene
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(
            dt=0.01,
            gravity=(0, 0, -9.81),
        ),
        viewer_options=gs.options.ViewerOptions(
            res=(1280, 720),
            max_FPS=60,
        ),
    )
    
    # Add ground plane
    scene.add_entity(gs.morphs.Plane())
    
    # Add a robot (using Franka Panda as example)
    robot = scene.add_entity(
        gs.morphs.URDF(
            file="gs://robots/franka_panda/panda.urdf",
            pos=(0, 0, 0.5),
            euler=(0, 0, 0),
        )
    )
    
    # Build scene
    scene.build()
    
    print("=== Genesis Link Kinematics API Demo ===\n")
    
    # 1. Get specific link by name
    print("1. Getting specific link:")
    end_effector = robot.get_link("panda_hand")
    print(f"   End effector link: {end_effector}")
    print(f"   Link index: {end_effector.idx_local}")
    
    # 2. Get all link positions and orientations
    print("\n2. Getting all link positions and orientations:")
    links_pos = robot.get_links_pos()  # Shape: (n_links, n_envs, 3)
    links_quat = robot.get_links_quat()  # Shape: (n_links, n_envs, 4)
    print(f"   Number of links: {robot.n_links}")
    print(f"   Links positions shape: {links_pos.shape}")
    print(f"   Links quaternions shape: {links_quat.shape}")
    
    # Print first few link positions
    for i in range(min(3, robot.n_links)):
        print(f"   Link {i} position: {links_pos[i, 0]}")
        print(f"   Link {i} quaternion: {links_quat[i, 0]}")
    
    # 3. Get specific link position and orientation
    print("\n3. Getting end effector position and orientation:")
    ee_pos = end_effector.get_pos()  # Shape: (n_envs, 3)
    ee_quat = end_effector.get_quat()  # Shape: (n_envs, 4)
    print(f"   End effector position: {ee_pos[0]}")
    print(f"   End effector quaternion: {ee_quat[0]}")
    
    # 4. Get current joint positions
    print("\n4. Current joint configuration:")
    qpos = robot.get_dofs_position()  # Shape: (n_dofs, n_envs)
    print(f"   Number of DOFs: {robot.n_dofs}")
    print(f"   Joint positions: {qpos[:, 0]}")
    
    # 5. Forward kinematics with different joint configurations
    print("\n5. Forward kinematics with different joint configurations:")
    
    # Example joint configuration 1
    qpos_test1 = np.zeros((robot.n_dofs, 1))
    qpos_test1[0] = 0.5  # Rotate first joint
    qpos_test1[1] = -0.3  # Rotate second joint
    
    pos1, quat1 = robot.forward_kinematics(qpos_test1)
    print(f"   Test config 1 - End effector pos: {pos1[-1, 0]}")
    print(f"   Test config 1 - End effector quat: {quat1[-1, 0]}")
    
    # Example joint configuration 2
    qpos_test2 = np.zeros((robot.n_dofs, 1))
    qpos_test2[0] = -0.5
    qpos_test2[1] = 0.3
    qpos_test2[2] = 0.2
    
    pos2, quat2 = robot.forward_kinematics(qpos_test2)
    print(f"   Test config 2 - End effector pos: {pos2[-1, 0]}")
    print(f"   Test config 2 - End effector quat: {quat2[-1, 0]}")
    
    # 6. Transform between link positions
    print("\n6. Computing transforms between links:")
    
    # Get base link position
    base_pos = robot.get_pos()  # Base link position
    base_quat = robot.get_quat()  # Base link orientation
    
    # Compute relative position of end effector w.r.t base
    ee_relative_pos = ee_pos[0] - base_pos[0]
    print(f"   End effector relative to base: {ee_relative_pos}")
    
    # 7. Visualize link positions during simulation
    print("\n7. Running simulation and tracking link positions...")
    
    # Set initial joint configuration
    robot.set_dofs_position(qpos_test1[:, 0])
    
    # Run simulation for a few steps
    for i in range(100):
        # Apply some control
        if i == 50:
            robot.set_dofs_position(qpos_test2[:, 0])
        
        # Step simulation
        scene.step()
        
        # Track end effector position every 20 steps
        if i % 20 == 0:
            ee_pos_current = end_effector.get_pos()[0]
            print(f"   Step {i}: End effector at {ee_pos_current}")
    
    # 8. Using forward kinematics for trajectory planning
    print("\n8. Forward kinematics for trajectory visualization:")
    
    # Create a simple joint space trajectory
    n_waypoints = 5
    trajectory = []
    for i in range(n_waypoints):
        alpha = i / (n_waypoints - 1)
        qpos_interp = (1 - alpha) * qpos_test1 + alpha * qpos_test2
        trajectory.append(qpos_interp)
    
    # Compute end effector positions along trajectory
    ee_trajectory = []
    for qpos in trajectory:
        pos, quat = robot.forward_kinematics(qpos)
        ee_trajectory.append(pos[-1, 0])  # Last link is end effector
    
    print("   End effector trajectory:")
    for i, ee_pos in enumerate(ee_trajectory):
        print(f"   Waypoint {i}: {ee_pos}")
    
    # Optional: Visualize the trajectory
    if scene.viewer is not None:
        # Draw the planned path
        scene.draw_debug_path(
            qposs=np.array(trajectory)[:, :, 0],  # Convert to expected format
            entity=robot,
            link_idx=-1,  # Use last link (end effector)
            density=0.3,
            frame_scaling=0.1
        )
    
    print("\n=== Demo Complete ===")
    
    # Keep viewer open if running interactively
    if scene.viewer is not None:
        while scene.viewer.is_alive():
            scene.step()


if __name__ == "__main__":
    main()