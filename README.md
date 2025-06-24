# Genesis Humanoid Learning

A comprehensive framework for humanoid robot simulation and learning using the Genesis physics engine. This project provides tools for automatic robot grounding, parallel environments, and advanced physics simulation with the UNITREE G1 humanoid robot.

## 🚀 Features

- **Automatic Robot Grounding**: Intelligent positioning system that automatically calculates proper ground placement for humanoid robots
- **High-Performance Physics**: Ultra-fast GPU-accelerated simulation (100+ FPS) with Genesis physics engine
- **Parallel Environments**: Support for multiple robot instances for reinforcement learning
- **Video Recording**: Built-in recording capabilities for all simulations
- **Comprehensive Samples**: 4 core demonstration programs showcasing different capabilities

## 📋 Requirements

- Python 3.8+
- NVIDIA GPU with CUDA support
- Genesis physics engine
- PyTorch

## 🛠️ Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/jkoba0512/genesis_humanoid_learning.git
cd genesis_humanoid_learning

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Run a sample
uv run python samples/01_basic_visualization.py
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/jkoba0512/genesis_humanoid_learning.git
cd genesis_humanoid_learning

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Genesis
pip install genesis-world

# Install other dependencies
pip install torch numpy
```

## 🎮 Quick Start

### 1. Basic Visualization
```bash
uv run python samples/01_basic_visualization.py
```
Loads and visualizes the UNITREE G1 robot with automatic grounding.

### 2. Robot Control Demo
```bash
uv run python samples/02_robot_control.py
```
Demonstrates joint control with multiple motion patterns.

### 3. Parallel Environments
```bash
uv run python samples/03_parallel_environments.py
```
Shows 4 robots running different motion patterns simultaneously.

### 4. Advanced Physics
```bash
uv run python samples/04_advanced_physics.py
```
Demonstrates high-fidelity physics with collision detection and solver accuracy.

## 🤖 Robot Grounding Library

The `robot_grounding` module provides automatic height calculation for stable robot placement:

```python
from robot_grounding import RobotGroundingCalculator

# Initialize calculator
calculator = RobotGroundingCalculator(robot, verbose=True)

# Get optimal ground height
grounding_height = calculator.get_grounding_height(safety_margin=0.03)

# Position robot
robot.set_pos(torch.tensor([0, 0, grounding_height], device='cuda:0'))
```

### Key Features:
- **URDF Analysis**: Automatically detects foot links from robot structure
- **Forward Kinematics**: Calculates exact distance from base to ground
- **Safety Margins**: Prevents ground penetration with configurable clearance
- **Multi-Robot Support**: Works with parallel environments

## 📁 Project Structure

```
genesis_humanoid_learning/
├── robot_grounding/        # Automatic grounding library
│   ├── __init__.py
│   ├── calculator.py       # Main grounding calculator
│   ├── detector.py         # Foot link detection
│   └── utils.py           # Utility functions
├── samples/               # Core demonstration programs
│   ├── 01_basic_visualization.py
│   ├── 02_robot_control.py
│   ├── 03_parallel_environments.py
│   └── 04_advanced_physics.py
├── examples/              # Additional examples
├── assets/                # Robot models and meshes
│   └── robots/g1/        # UNITREE G1 robot files
└── docs/                  # Documentation
```

## 🎥 Video Recording

All samples include automatic video recording:
- Videos saved to `samples/videos/`
- 1280x720 resolution at 60 FPS
- Automatic timestamp naming

## 🔧 Configuration

### Simulation Parameters
```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,           # Timestep
        substeps=10,       # Physics substeps
    ),
    viewer_options=gs.options.ViewerOptions(
        res=(1280, 720),   # Resolution
        max_FPS=60,        # Frame rate
    ),
)
```

### Robot Grounding Options
```python
# Safety margin (default: 30mm)
grounding_height = calculator.get_grounding_height(safety_margin=0.03)

# Verbose output
calculator = RobotGroundingCalculator(robot, verbose=True)
```

## 📊 Performance

- **Single Robot**: 100-200 FPS (RTX 3060 Ti)
- **4 Parallel Robots**: 30-40 FPS total
- **Physics Accuracy**: High-fidelity with CG solver
- **GPU Memory**: ~2-3 GB per scene

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project uses the UNITREE G1 robot model under BSD-3-Clause license.

## 🙏 Acknowledgments

- Genesis physics engine team for the ultra-fast simulation platform
- UNITREE Robotics for the G1 humanoid robot model
- Robot descriptions package for standardized URDF formats

## 📚 Additional Resources

- [Genesis Documentation](https://genesis-world.readthedocs.io/)
- [CLAUDE.md](CLAUDE.md) - Detailed project instructions and API notes
- [Sample Videos](samples/videos/) - Generated simulation recordings