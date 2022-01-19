from brep_to_h5m import brep_to_h5m

brep_to_h5m(
    brep_filename="my_brep_file_with_merged_surfaces.brep",
    volumes_with_tags={
        # 1: 'material_for_volume_1', # removed plasma as not many interactions occur here
        2: "material_for_volume_2",
        3: "material_for_volume_3",
        4: "material_for_volume_4",
        5: "material_for_volume_5",
        6: "material_for_volume_6",
        7: "material_for_volume_7",
        8: "material_for_volume_8",
    },
    h5m_filename="dagmc.h5m",
    min_mesh_size=1,
    max_mesh_size=10,
    mesh_algorithm=1,
)
