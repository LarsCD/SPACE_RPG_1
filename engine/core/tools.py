"""
simple tools to help other pieces of the engine


"""

def mouse_to_world(mouse_x, mouse_y, radar_center, player, scale):
    cx, cy = radar_center
    dx = mouse_x - cx
    dy = mouse_y - cy
    world_dx = -dy / scale
    world_dy = dx / scale
    px, py = player.coordinates
    return px + world_dx, py + world_dy
