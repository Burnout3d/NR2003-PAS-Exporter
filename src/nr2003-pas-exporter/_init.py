## ***** BEGIN GPL LICENSE BLOCK ***** 
# 
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program; if not, write to the Free Software Foundation, 
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. 
# 
# ***** END GPL LICENCE BLOCK *****
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator

class ExportPapyrus(Operator, ExportHelper):
    bl_idname = "export_scene.pas"
    bl_label = "Export Papyrus ASCII Format"
    
    filename_ext = ".pas"
    
    filter_glob: StringProperty(
        default="*.pas",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    export_type: EnumProperty(
        name="Export Type",
        description="Choose what to export",
        items=(
            ('ALL', "All Objects", "Export all objects in the scene"),
            ('SELECTED', "Selected Objects", "Export selected objects"),
            ('VISIBLE', "Visible Objects", "Export visible objects"),
        ),
        default='ALL',
    )
    
    def execute(self, context):
        filepath = self.filepath
        export_type = self.export_type
        
        objects = []
        if export_type == 'ALL':
            objects = context.scene.objects
        elif export_type == 'SELECTED':
            objects = context.selected_objects
        elif export_type == 'VISIBLE':
            objects = [obj for obj in context.scene.objects if obj.visible_get()]
        
        with open(filepath, 'w') as file:
            file.write("VERSION\t200\n")
            file.write("UNIT_CONVERSION\t1.000000\n")
            
            for obj in objects:
                if obj.type == 'MESH':
                    file.write('NAME "{}"\n'.format(obj.name))
                    file.write("\tTRANSFORM {\n")
                    for i in range(4):
                        row = obj.matrix_world[i]
                        formatted_row = '\t'.join(f'{value:.5f}' for value in row)
                        file.write('\t\tXFORM_ROW{} {}\n'.format(i, formatted_row))
                    formatted_location = '\t'.join(f'{value:.5f}' for value in obj.location)
                    file.write('\t\tXFORM_ROW3 {}\n'.format(formatted_location))
                    file.write('\t\tXFORM_POS {}\n'.format(formatted_location))
                    file.write("\t}\n")
                    
                    mesh = obj.data
                    file.write("\tMESH {\n")
                    file.write("\t\tNUM_VERTICES {}\n".format(len(mesh.vertices)))
                    file.write("\t\tVERTEX_LIST {\n")
                    for i, v in enumerate(mesh.vertices):
                        file.write('\t\t\tVERTEX {}:\t{:.5f}\t{:.5f}\t{:.5f}\n'.format(i, v.co.x, v.co.y, v.co.z))
                    file.write("\t\t}\n")
                    
                    file.write("\t\tNUM_FACES {}\n".format(len(mesh.polygons)))
                    file.write("\t\tFACE_LIST {\n")
                    for i, p in enumerate(mesh.polygons):
                        verts = ' '.join(map(str, p.vertices))
                        file.write('\t\t\tFACE {}: {}\n'.format(i, verts))
                    file.write("\t\t}\n")
                    
                    file.write("\t\tNORMAL_LIST {\n")
                    for i, p in enumerate(mesh.polygons):
                        normal = p.normal
                        file.write('\t\t\tFACE_NORMAL {}: 1 {:.5f}\t{:.5f}\t{:.5f}\n'.format(i, normal.x, normal.y, normal.z))
                        for j, v in enumerate(p.vertices):
                            normal = mesh.vertices[v].normal
                            file.write('\t\t\t\tVERTEX_NORMAL {}\t{:.5f}\t{:.5f}\t{:.5f}\n'.format(v, normal.x, normal.y, normal.z))
                    file.write("\t\t}\n")
                    
                    if len(obj.material_slots) > 0:
                        file.write("\t\tNUM_MATERIAL_REFS 1\n")
                        file.write("\t\tMATERIAL_REF {\n")
                        mat = obj.material_slots[0].material
                        file.write('\t\t\tMATERIAL {\n')
                        file.write('\t\t\t\tNAME "{}"\n'.format(mat.name))
                        
                        if "Emission" in mat.node_tree.nodes:
                            file.write('\t\t\t\tMATERIAL_AMBIENT {:.5f}\n'.format(mat.node_tree.nodes["Emission"].inputs["Strength"].default_value))
                        else:
                            file.write('\t\t\t\tMATERIAL_AMBIENT 0.0\n')
                        
                        if "Principled BSDF" in mat.node_tree.nodes:
                            base_color = mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value[:3]
                            file.write('\t\t\t\tMATERIAL_DIFFUSE {:.5f} {:.5f} {:.5f}\n'.format(*base_color))
                            file.write('\t\t\t\tMATERIAL_SPECULAR {:.5f}\n'.format(mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value))
                            file.write('\t\t\t\tMATERIAL_SHININESS {:.5f}\n'.format(mat.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value))
                            file.write('\t\t\t\tMATERIAL_REFLECTIVITY {:.5f}\n'.format(mat.node_tree.nodes["Principled BSDF"].inputs["Coat Roughness"].default_value))
                            file.write('\t\t\t\tMATERIAL_OPACITY {:.5f}\n'.format(mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value))
                        else:
                            file.write('\t\t\t\tMATERIAL_DIFFUSE 0.0 0.0 0.0\n')
                            file.write('\t\t\t\tMATERIAL_SPECULAR 0.0\n')
                            file.write('\t\t\t\tMATERIAL_SHININESS 0.0\n')
                            file.write('\t\t\t\tMATERIAL_REFLECTIVITY 0.0\n')
                            file.write('\t\t\t\tMATERIAL_OPACITY 1.0\n')
                        
                        if "Image Texture" in mat.node_tree.nodes:
                            file.write('\t\t\t\tBASE_TEXTURE "{}"\tDISABLE_ALPHA\n'.format(mat.node_tree.nodes["Image Texture"].image.filepath))
                        else:
                            file.write('\t\t\t\tBASE_TEXTURE ""\n')
                        
                        if "Roughness Map" in mat.node_tree.nodes:
                            file.write('\t\t\t\tSHININESS_MAP_TEXTURE "{}"\tDISABLE_ALPHA\n'.format(mat.node_tree.nodes["Roughness Map"].image.filepath))
                        
                        if "Background" in context.scene.world.node_tree.nodes:
                            file.write('\t\t\t\tENVIRONMENT_MAP_TEXTURE "{}"\tDISABLE_ALPHA\n'.format(context.scene.world.node_tree.nodes["Background"].inputs["Color"].default_value))
                        
                        file.write("\t\t\t}\n")
                        file.write("\t\t\tNUM_FACES {}\n".format(len(mesh.polygons)))
                        
                        uv_layer = mesh.uv_layers.active.data if mesh.uv_layers.active else None
                        for i, p in enumerate(mesh.polygons):
                            if uv_layer:
                                uv_coords = [uv_layer[loop_index].uv for loop_index in p.loop_indices]
                                base_texture_coords = ' '.join(f'({uv.x:.4f}, {uv.y:.4f})' for uv in uv_coords)
                                shininess_map_coords = base_texture_coords  # Assuming the same UVs for shininess map
                            else:
                                base_texture_coords = "(0.0, 0.0) (0.0, 0.0) (0.0, 0.0)"
                                shininess_map_coords = base_texture_coords
                            
                            file.write(f'\t\t\tTEXTURE_FACE {i} BASE_TEXTURE {base_texture_coords} SHININESS_MAP_TEXTURE {shininess_map_coords}\n')
                        file.write("\t\t}\n")
                    else:
                        file.write("\t\tNUM_MATERIAL_REFS 0\n")
                    file.write("\t}\n")



        return {'FINISHED'}

def menu_func_export(self, context):
    self.layout.operator(ExportPapyrus.bl_idname, text="Papyrus ASCII Format (.pas)")

def register():
    bpy.utils.register_class(ExportPapyrus)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportPapyrus)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
