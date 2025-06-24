# Genesis Learning Samples

Learn Genesis framework through practical examples with Unitree G1 humanoid robot. All samples include fallback options for other robot models.

## Setup

### Dependencies
```bash
uv add genesis-world numpy torch
uv add --dev black ruff pytest
```

### Robot Model
Place Unitree G1 URDF file at: `assets/robots/g1/g1.urdf`
Download from [robot-descriptions](https://github.com/robot-descriptions/g1-description)

## Samples

### 01_basic_visualization.py
**Basic Visualization**
- Genesis initialization and scene creation
- URDF robot loading with automatic grounding
- Interactive visualization and controls

```bash
uv run python samples/01_basic_visualization.py
```

### 02_robot_control.py
**Robot Control**
- Joint position control and state reading
- Motion patterns (oscillation, walking-like)
- DOF manipulation with automatic grounding

```bash
uv run python samples/02_robot_control.py
```

### 03_parallel_environments.py
**Parallel Environments**
- Multiple parallel simulation environments
- Batch robot control with different motion patterns
- Performance optimization for RL training

```bash
uv run python samples/03_parallel_environments.py
```

### 04_advanced_physics.py
**Advanced Physics**
- High-accuracy physics solvers and contact forces
- Self-collision detection and joint limits
- Material properties and physics monitoring

```bash
uv run python samples/04_advanced_physics.py
```

## Key Features

- **Automatic Robot Grounding**: All samples use robot_grounding library for proper foot placement
- **Fallback Support**: Automatic fallback to box models if G1 URDF not available
- **Interactive Controls**: Mouse rotation, scroll zoom, ESC exit, Space pause
- **Performance Monitoring**: Real-time simulation statistics and robot state tracking

## Troubleshooting

**No G1 URDF**: Samples automatically use fallback box models
**Performance**: Reduce parallel environments, adjust timesteps
**Display Issues**: Set `show_viewer=False` for headless operation

## Next Steps

1. Create custom environments for specific tasks
2. Integrate with reinforcement learning frameworks  
3. Implement advanced control algorithms
4. Add sensor simulations (cameras, LiDAR)