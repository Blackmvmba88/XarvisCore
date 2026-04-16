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


import bpy
import os


class XarvisAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    require_token: bpy.props.BoolProperty(
        name="Require Token",
        description="Require token file for privileged commands (render/export/operator)",
        default=False,
    )

    token_path: bpy.props.StringProperty(
        name="Token Path",
        description="Path to token file (read-only in UI)",
        default="~/.config/xarvis/blender.token",
    )

    use_frame_hooks: bpy.props.BoolProperty(
        name="Use Blender Frame Hooks (experimental)",
        description="Allow addon to subscribe to Blender's frame_change_post handler to improve render progress reporting",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "require_token")
        row = layout.row()
        row.prop(self, "token_path")
        if self.require_token and not os.path.exists(os.path.expanduser(self.token_path)):
            row = layout.row()
            row.label(text="Warning: Token file not found at token path", icon="ERROR")
        layout.separator()
        layout.prop(self, "use_frame_hooks")
        if self.use_frame_hooks:
            row = layout.row()
            row.label(text="Experimental: frame hooks are best-effort and opt-in", icon='INFO')


def register():
    bpy.utils.register_class(XarvisAddonPreferences)
    # Start the local server when the addon is enabled in Blender
    server.start_server()


def unregister():
    # Stop the server when the addon is disabled
    server.stop_server()
    bpy.utils.unregister_class(XarvisAddonPreferences)
