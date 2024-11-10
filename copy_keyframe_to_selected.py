import bpy
from bpy.types import Operator, Panel

bl_info = {
    "name": "Copy Keyframe to Selected Objects",
    "blender": (4, 1, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "author": "Unlim8ted Studio Productions",
    "description": "Copy the current keyframe to all selected objects."
}

# Define the operator to copy the keyframe to selected objects
class OBJECT_OT_copy_keyframe_to_selected(Operator):
    bl_idname = "object.copy_keyframe_to_selected"
    bl_label = "Copy Keyframe to Selected"
    bl_description = "Copy the current keyframe of the specified property to all selected objects at this frame"

    # Properties for user input with tooltips
    data_path: bpy.props.StringProperty(
        name="Data Path",
        description="The data path of the property to keyframe (e.g., 'location' for position, 'rotation_euler' for rotation, 'scale' for scaling)"
    )
    array_index: bpy.props.IntProperty(
        name="Array Index",
        default=0,
        description="Index for array properties (e.g., 0 for X, 1 for Y, 2 for Z for 'location', 'rotation_euler', or 'scale')"
    )

    def execute(self, context):
        active_obj = context.active_object
        selected_objects = context.selected_objects
        frame = context.scene.frame_current

        if not active_obj or not selected_objects:
            self.report({'WARNING'}, "No active or selected objects.")
            return {'CANCELLED'}

        # Ensure there's animation data and an action with FCurves on the active object
        action = active_obj.animation_data.action if active_obj.animation_data else None
        if not action:
            self.report({'WARNING'}, "No keyframe data found on the active object.")
            return {'CANCELLED'}

        # Locate the FCurve for the specified property and index
        fcurve = action.fcurves.find(self.data_path, index=self.array_index)
        if not fcurve:
            self.report({'WARNING'}, "No keyframe found on the specified property.")
            return {'CANCELLED'}

        # Evaluate the FCurve to get the value at the current frame
        value = fcurve.evaluate(frame)

        # Copy the keyframe value to each selected object
        for obj in selected_objects:
            if obj != active_obj:
                if not obj.animation_data:
                    obj.animation_data_create()
                if not obj.animation_data.action:
                    obj.animation_data.action = bpy.data.actions.new(name=f"{obj.name}_Action")

                # Find or create the FCurve on the target object
                target_fcurve = obj.animation_data.action.fcurves.find(self.data_path, index=self.array_index)
                if not target_fcurve:
                    target_fcurve = obj.animation_data.action.fcurves.new(data_path=self.data_path, index=self.array_index)

                # Insert the keyframe at the current frame
                target_fcurve.keyframe_points.insert(frame, value, options={'FAST'})

        return {'FINISHED'}

# Add the operator to the N-panel for easy access
class VIEW3D_PT_copy_keyframe_to_selected(Panel):
    bl_label = "Copy Keyframe to Selected"
    bl_idname = "VIEW3D_PT_copy_keyframe_to_selected"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Instructions:", icon='INFO')
        layout.label(text="1. Enter the Data Path for the property.")
        layout.label(text="   Common paths are:", icon='DOT')
        layout.label(text="   - 'location' for position (X, Y, Z)")
        layout.label(text="   - 'rotation_euler' for rotation (X, Y, Z)")
        layout.label(text="   - 'scale' for scaling (X, Y, Z)")
        layout.label(text="2. Set Array Index for specific axis:")
        layout.label(text="   - 0 for X, 1 for Y, 2 for Z")
        layout.label(text="you can also right click on an ")
        layout.label(text="animated property in the")
        layout.label(text="properties window and click")
        layout.label(text="'copy data path' to get the Data Path.")

        layout.prop(context.scene, "copy_keyframe_data_path", text="Data Path")
        layout.prop(context.scene, "copy_keyframe_array_index", text="Array Index")

        op = layout.operator(OBJECT_OT_copy_keyframe_to_selected.bl_idname, text="Copy Keyframe to Selected")
        op.data_path = context.scene.copy_keyframe_data_path
        op.array_index = context.scene.copy_keyframe_array_index

# Register and add the operator to the N-panel
def register():
    bpy.utils.register_class(OBJECT_OT_copy_keyframe_to_selected)
    bpy.utils.register_class(VIEW3D_PT_copy_keyframe_to_selected)
    bpy.types.Scene.copy_keyframe_data_path = bpy.props.StringProperty(
        name="Data Path",
        default="location",
        description="Path to the property to keyframe (e.g., 'location', 'rotation_euler', 'scale')"
    )
    bpy.types.Scene.copy_keyframe_array_index = bpy.props.IntProperty(
        name="Array Index",
        default=0,
        description="Index for array properties (0 for X, 1 for Y, 2 for Z)"
    )

def unregister():
    del bpy.types.Scene.copy_keyframe_data_path
    del bpy.types.Scene.copy_keyframe_array_index
    bpy.utils.unregister_class(VIEW3D_PT_copy_keyframe_to_selected)
    bpy.utils.unregister_class(OBJECT_OT_copy_keyframe_to_selected)

if __name__ == "__main__":
    register()

# Script developed by Unlim8ted Studio Productions for Blender use
