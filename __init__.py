# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "SJ Handy Nator",
    "author": "CaptainHansode",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location":  "View3D > Sidebar > Tool Tab",
    "description": "My Tools.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Animation",
}


import bpy
from bpy.app.handlers import persistent


def sj_set_parent(self, context):
    """set parent"""
    if len(context.selected_objects) == 0:
        self.obj_parnet = None
    for obj in bpy.context.selected_objects:
        wmx = obj.matrix_world
        obj.parent = self.obj_parnet
        # これだと逆行列が適応されてしまうのでダメ
        # obj.matrix_parent_inverse = actor_offset_root.matrix_world.inverted()
        obj.matrix_world = wmx


@persistent
def callback_get_parent(self):
    """get parent callbacks"""
    if len(bpy.context.selected_objects) != 0:
        pass
        # bpy.context.scene.sj_handy_nator_props.obj_parnet = bpy.context.selected_objects[0].parent
    else:
        bpy.context.scene.sj_handy_nator_props.obj_parnet = None


class SJHandyNatorProperties(bpy.types.PropertyGroup):
    r"""カスタムプロパティを定義する"""
    # obj_parnet: bpy.props.StringProperty(name="Parent", update=set_parent)
    obj_parnet: bpy.props.PointerProperty(name="Parent", type=bpy.types.Object, update=sj_set_parent)


class SJHandySelTree(bpy.types.Operator):
    """Select Tree"""
    bl_idname = "sj_tools.sj_handy_nator_sel_tree"
    bl_label = "Tree Select"

    @classmethod
    def poll(cls, context):
        r""""""
        return context.active_object is not None

    def _get_children(self, c_objs):
        r"""ツリーを再帰回収"""
        ret = []
        for obj in c_objs:
            ret.append(obj)
            if len(obj.children) != 0:
                # 再帰
                ret.extend(self._get_children(obj.children))
        return ret

    def execute(self, context):
        r""""""
        sjsb = context.scene.sj_handy_nator_props
        sel_list = []
        sel_objs = {}
        for obj in context.selected_objects:  # 選択したオブジェクト
            if len(obj.children) != 0:
                sel_list.extend(self._get_children(obj.children))
        for obj in sel_list:
            obj.select_set(True)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)  # 再描画
        return {'FINISHED'}


class SJHandyLy(object):
    r"""set lay"""
    def __init__(self, *args, **kwargs):
        if len(bpy.context.selected_pose_bones) == 0:
            return None
        b = bpy.context.selected_pose_bones[-0]
        sw = bpy.context.object.data.bones[b.name].layers[args[0]]

        self.set_bone_layer(
            bpy.context.selected_pose_bones, [args[0]], not(sw))
        return None

    def set_bone_layer(self, pbn_list=[], ly_list=[0], sw=True):
        r"""set bone layers"""
        # 一旦レイヤー状態を保存
        saved_layers = [
            layer_bool for layer_bool in bpy.context.active_object.data.layers]
        # 表示
        for ly in range(0, 32):
            bpy.context.active_object.data.layers[ly] = True
        
        for pbn in pbn_list:
            for ly in ly_list:
                bpy.context.object.data.bones[pbn.name].layers[ly] = sw
        
        # 表示状態を復元して終わり
        for i, layer_bool in enumerate(saved_layers):
            bpy.context.active_object.data.layers[i] = layer_bool

        return True


class SJHandyNator(bpy.types.Panel):
    """UI"""
    bl_label = "SJ Handy Nator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'  # UIのタイプ
    # bl_context = "posemode"  # カスタムタブは名前を指定するだけで問題ない 他のツールのタブにも追加できる
    bl_category = 'Tool'
    # bl_category = 'SJTools'
    bl_options = {'DEFAULT_CLOSED'}  # デフォルトでは閉じている

    def draw(self, context):
        layout = self.layout
        sj_prop = context.scene.sj_handy_nator_props
        layout.label(text="Parent")
        col = layout.column()
        col.scale_y = 1.0
        col.operator(SJHandySelTree.bl_idname, text="Select Tree")
        # col.prop_search(sj_prop, "obj_parnet", bpy.data, "objects")
        col.prop_search(sj_prop, "obj_parnet", context.scene, "objects")


classes = (
    SJHandyNatorProperties,
    SJHandyNator,
    SJHandySelTree)


# Register all operators and panels
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.sj_handy_nator_props = bpy.props.PointerProperty(
        type=SJHandyNatorProperties)
    
    # add callback
    bpy.app.handlers.depsgraph_update_post.append(callback_get_parent)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.sj_handy_nator_props
    bpy.app.handlers.depsgraph_update_post.remove(callback_get_parent)


if __name__ == "__main__":
    register()
