# Genesis Kinematics API Reference

This document provides a comprehensive guide to Genesis API methods for accessing link positions, transforms, and forward kinematics.

## Core API Methods

### 1. Link Access Methods

#### `robot.get_link(name: str) -> RigidLink`
Get a specific link by name.

```python
# Example
end_effector = robot.get_link("panda_hand")
left_foot = humanoid.get_link("left_foot")
```

### 2. Position and Orientation Methods

#### `robot.get_links_pos(ls_idx_local=None, envs_idx=None) -> np.ndarray`
Get positions of all links in the robot.

- **Returns**: Array of shape `(n_links, n_envs, 3)` containing XYZ positions
- **Parameters**:
  - `ls_idx_local`: Optional indices of specific links to query
  - `envs_idx`: Optional environment indices for multi-env simulations

```python
# Get all link positions
links_pos = robot.get_links_pos()  # Shape: (n_links, n_envs, 3)

# Get specific links
links_pos = robot.get_links_pos(ls_idx_local=[0, 5, 10])
```

#### `robot.get_links_quat(ls_idx_local=None, envs_idx=None) -> np.ndarray`
Get quaternion orientations of all links.

- **Returns**: Array of shape `(n_links, n_envs, 4)` containing quaternions (x, y, z, w)
- **Parameters**: Same as `get_links_pos`

```python
# Get all link orientations
links_quat = robot.get_links_quat()  # Shape: (n_links, n_envs, 4)
```

#### `link.get_pos(envs_idx=None) -> np.ndarray`
Get position of a specific link.

- **Returns**: Array of shape `(n_envs, 3)` containing XYZ positions

```python
# Get end effector position
ee_pos = end_effector.get_pos()  # Shape: (n_envs, 3)
```

#### `link.get_quat(envs_idx=None) -> np.ndarray`
Get quaternion orientation of a specific link.

- **Returns**: Array of shape `(n_envs, 4)` containing quaternions

```python
# Get end effector orientation
ee_quat = end_effector.get_quat()  # Shape: (n_envs, 4)
```

### 3. Base Link Methods

#### `robot.get_pos(envs_idx=None) -> np.ndarray`
Get position of the robot's base link.

```python
base_pos = robot.get_pos()  # Shape: (n_envs, 3)
```

#### `robot.get_quat(envs_idx=None) -> np.ndarray`
Get quaternion orientation of the robot's base link.

```python
base_quat = robot.get_quat()  # Shape: (n_envs, 4)
```

### 4. Forward Kinematics

#### `robot.forward_kinematics(qpos, qs_idx_local=None, ls_idx_local=None, envs_idx=None) -> Tuple[np.ndarray, np.ndarray]`
Compute forward kinematics to get link positions and orientations from joint positions.

- **Parameters**:
  - `qpos`: Joint positions array of shape `(n_dofs, n_envs)` or `(n_dofs,)`
  - `qs_idx_local`: Optional indices of specific joints
  - `ls_idx_local`: Optional indices of specific links to compute
  - `envs_idx`: Optional environment indices
- **Returns**: Tuple of (positions, quaternions)
  - `positions`: Shape `(n_links, n_envs, 3)`
  - `quaternions`: Shape `(n_links, n_envs, 4)`

```python
# Example: compute forward kinematics for a given joint configuration
qpos = np.array([0.5, -0.3, 0.0, -1.5, 0.0, 1.0, 0.0])  # 7 DOF
positions, quaternions = robot.forward_kinematics(qpos)

# Get end effector pose
ee_pos = positions[-1, 0]  # Last link, first environment
ee_quat = quaternions[-1, 0]
```

### 5. Joint Configuration Methods

#### `robot.get_dofs_position(dofs_idx_local=None, envs_idx=None) -> np.ndarray`
Get current joint positions.

```python
qpos = robot.get_dofs_position()  # Shape: (n_dofs, n_envs)
```

#### `robot.set_dofs_position(qpos, dofs_idx_local=None, envs_idx=None)`
Set joint positions.

```python
robot.set_dofs_position(target_qpos)
```

## Utility Functions

### Transform Utilities
Genesis provides utility functions in `genesis.utils.geom` for working with transforms:

```python
import genesis.utils.geom as gu

# Convert position and quaternion to transformation matrix
T = gu.trans_quat_to_T(pos, quat)

# Other useful utilities (if available):
# - Quaternion operations
# - Rotation conversions
# - Transform composition
```

## Common Use Cases

### 1. Getting End Effector Pose
```python
# Method 1: Direct link access
end_effector = robot.get_link("gripper")
ee_pos = end_effector.get_pos()[0]
ee_quat = end_effector.get_quat()[0]

# Method 2: Using link indices
links_pos = robot.get_links_pos()
ee_pos = links_pos[-1, 0]  # Assuming last link is end effector
```

### 2. Computing Relative Transforms
```python
# Get transform between two links
link1_pos = robot.get_link("link1").get_pos()[0]
link1_quat = robot.get_link("link1").get_quat()[0]

link2_pos = robot.get_link("link2").get_pos()[0]
link2_quat = robot.get_link("link2").get_quat()[0]

# Relative position
relative_pos = link2_pos - link1_pos
```

### 3. Trajectory Planning in Joint Space
```python
# Plan trajectory in joint space
trajectory = []
for t in np.linspace(0, 1, 100):
    qpos = qpos_start * (1 - t) + qpos_end * t
    trajectory.append(qpos)

# Compute end effector path
ee_path = []
for qpos in trajectory:
    pos, quat = robot.forward_kinematics(qpos)
    ee_path.append(pos[-1, 0])  # End effector position
```

### 4. Multi-Environment Queries
```python
# For parallel environments
n_envs = 10
scene.build(n_envs=n_envs)

# Get positions for all environments
links_pos = robot.get_links_pos()  # Shape: (n_links, n_envs, 3)

# Get positions for specific environments
links_pos = robot.get_links_pos(envs_idx=[0, 2, 5])
```

## Important Notes

1. **Coordinate Systems**: Positions are in world coordinates by default
2. **Quaternion Format**: Quaternions are in (x, y, z, w) format
3. **Array Shapes**: Most methods return arrays with environment dimension for parallel simulation support
4. **Link Indexing**: Link indices can be obtained via `link.idx_local`
5. **Performance**: Forward kinematics is computed on GPU when using CUDA backend

## Integration with Inverse Kinematics

While this document focuses on forward kinematics and link queries, Genesis also provides inverse kinematics:

```python
# Basic IK example
target_pos = np.array([0.5, 0.0, 0.3])
target_quat = np.array([0, 1, 0, 0])

qpos = robot.inverse_kinematics(
    link=end_effector,
    pos=target_pos,
    quat=target_quat
)
```

## Debugging and Visualization

Genesis provides visualization tools for debugging kinematics:

```python
# Draw planned path
scene.draw_debug_path(
    qposs=trajectory,
    entity=robot,
    link_idx=-1,  # End effector
    density=0.3,
    frame_scaling=0.1
)
```