import paramak
from brep_to_h5m import brep_to_h5m
import dagmc_h5m_file_inspector as di  # optional just used to inspect the file
import brep_part_finder as bpf


# creates a 3D model of a reactor with PF coils
my_reactor = paramak.BallReactor(
    inner_bore_radial_thickness=10,
    inboard_tf_leg_radial_thickness=30,
    center_column_shield_radial_thickness=60,
    divertor_radial_thickness=150,
    inner_plasma_gap_radial_thickness=30,
    plasma_radial_thickness=300,
    outer_plasma_gap_radial_thickness=30,
    plasma_gap_vertical_thickness=50,
    firstwall_radial_thickness=30,
    blanket_radial_thickness=50,
    blanket_rear_wall_radial_thickness=30,
    elongation=2,
    triangularity=0.55,
    rotation_angle=180,
    pf_coil_case_thicknesses=[10, 10, 10, 12],
    pf_coil_radial_thicknesses=[20, 50, 50, 20],
    pf_coil_vertical_thicknesses=[20, 50, 50, 20],
    pf_coil_radial_position=[500, 575, 575, 500],
    pf_coil_vertical_position=[300, 100, -100, -300],
    # number_of_tf_coils=16,
    # rear_blanket_to_tf_gap=50,
    # outboard_tf_coil_radial_thickness=100,
    # outboard_tf_coil_poloidal_thickness=50
)


# saves the reactor as a Brep file with merged surfaces
my_reactor.export_brep("my_brep_file_with_merged_surfaces.brep")

# brep file is imported
my_brep_part_properties = bpf.get_brep_part_properties(
    "my_brep_file_with_merged_surfaces.brep"
)

# request to find part ids that are mixed up in the Brep file
# using the volume, center, bounding box that we know about when creating the
# CAD geometry in the first place
key_and_part_id = bpf.get_dict_of_part_ids(
    brep_part_properties=my_brep_part_properties,
    shape_properties=my_reactor.part_properties,
)

key_and_part_id = {key: val for key, val in key_and_part_id.items() if val != "plasma"}
print(key_and_part_id)

brep_to_h5m(
    brep_filename="my_brep_file_with_merged_surfaces.brep",
    volumes_with_tags=key_and_part_id,
    h5m_filename="dagmc.h5m",
    min_mesh_size=20,
    max_mesh_size=30,  # reduce this number for an improved mesh
)

tags = di.get_materials_from_h5m("dagmc.h5m")

# each tag will need a material definition in OpenMC
print("material tags within DAGMC h5m file", tags)
