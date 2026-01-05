bl_info = {
    "name": "Xarvis Connector Addon",
    "author": "Blackmvmba88",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "Preferences > Add-ons",
    "description": "Expose a small local JSON-RPC HTTP server inside Blender for interactive control",
    "category": "Development",
}

# Minimal addon entrypoints — keeps server lifecycle tied to register/unregister

from . import server


def register():
    # Start the local server when the addon is enabled in Blender
    server.start_server()


def unregister():
    # Stop the server when the addon is disabled
    server.stop_server()
