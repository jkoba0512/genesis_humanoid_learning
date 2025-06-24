#!/usr/bin/env python3
"""
Debug script to explore robot link structure.
"""

import genesis as gs


def main():
    print("=== Robot Link Structure Debug ===\n")
    
    # Initialize Genesis
    gs.init()
    
    # Create scene
    scene = gs.Scene(show_viewer=False)
    plane = scene.add_entity(gs.morphs.Plane())
    
    # Load robot
    try:
        robot = scene.add_entity(
            gs.morphs.URDF(
                file="assets/robots/g1/g1.urdf",
                pos=(0, 0, 1.0),
            ),
        )
        
        print(f"Robot loaded: {robot.n_links} links, {robot.n_dofs} DOFs\n")
        
        # Explore link structure
        print("=== All Links ===")
        for i, link in enumerate(robot.links):
            # Check available attributes
            attrs = []
            if hasattr(link, 'name'):
                attrs.append(f"name='{link.name}'")
            if hasattr(link, 'idx'):
                attrs.append(f"idx={link.idx}")
            if hasattr(link, 'parent_idx'):
                attrs.append(f"parent_idx={link.parent_idx}")
            
            print(f"Link {i}: {', '.join(attrs)}")
        
        print("\n=== Checking for end links ===")
        # Find links with no children - use link.idx instead of list index
        all_parent_idxs = set()
        for link in robot.links:
            if hasattr(link, 'parent_idx') and link.parent_idx >= 0:
                all_parent_idxs.add(link.parent_idx)
        
        end_links = []
        for link in robot.links:
            if hasattr(link, 'idx') and link.idx not in all_parent_idxs:
                end_links.append(link)
        
        print(f"Found {len(end_links)} end links:")
        for link in end_links:
            name = link.name if hasattr(link, 'name') else 'unnamed'
            print(f"  - {name} (idx={link.idx})")
        
        # Check specifically for ankle links
        print("\n=== Looking for ankle/foot links ===")
        for link in robot.links:
            if hasattr(link, 'name'):
                name_lower = link.name.lower()
                if 'ankle' in name_lower or 'foot' in name_lower:
                    print(f"  - {link.name} (idx={link.idx}, parent_idx={link.parent_idx})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()