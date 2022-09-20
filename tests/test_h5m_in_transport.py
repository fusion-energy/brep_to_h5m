from vertices_to_h5m import vertices_to_h5m
from pathlib import Path
import dagmc_h5m_file_inspector as di
import openmc
import openmc_data_downloader as odd
from brep_to_h5m import brep_to_h5m
import math


"""
Tests that check that:
    - h5m files are created
    - h5m files contain the correct number of volumes
    - h5m files contain the correct material tags
    - h5m files can be used a transport geometry in DAGMC with OpenMC 
"""


def transport_particles_on_h5m_geometry(
    h5m_filename, material_tags, cross_sections_xml=None
):
    """A function for testing the geometry file with particle transport in DAGMC OpenMC"""

    materials = openmc.Materials()
    for material_tag in material_tags:

        # simplified material definitions have been used to keen this example minimal
        mat_dag_material_tag = openmc.Material(name=material_tag)
        mat_dag_material_tag.add_element("H", 1, "ao")
        mat_dag_material_tag.set_density("g/cm3", 1e-5)

        materials.append(mat_dag_material_tag)

    if cross_sections_xml:
        materials.cross_sections = cross_sections_xml
    # downloads the nuclear data and sets the openmc_cross_sections environmental variable
    odd.just_in_time_library_generator(libraries="ENDFB-7.1-NNDC", materials=materials)

    dag_univ = openmc.DAGMCUniverse(filename=h5m_filename)
    bound_dag_univ = dag_univ.bounded_universe()
    geometry = openmc.Geometry(root=bound_dag_univ)

    # initializes a new source object
    my_source = openmc.Source()

    center_of_geometry = (
        (dag_univ.bounding_box[0][0] + dag_univ.bounding_box[1][0]) / 2,
        (dag_univ.bounding_box[0][1] + dag_univ.bounding_box[1][1]) / 2,
        (dag_univ.bounding_box[0][2] + dag_univ.bounding_box[1][2]) / 2,
    )
    # sets the location of the source which is not on a vertex
    center_of_geometry_nudged = (
        center_of_geometry[0] + 0.1,
        center_of_geometry[1] + 0.1,
        center_of_geometry[2] + 0.1,
    )

    print("center_of_geometry", center_of_geometry)

    my_source.space = openmc.stats.Point(center_of_geometry_nudged)
    # sets the direction to isotropic
    my_source.angle = openmc.stats.Isotropic()
    # sets the energy distribution to 100% 14MeV neutrons
    my_source.energy = openmc.stats.Discrete([14e6], [1])

    # specifies the simulation computational intensity
    settings = openmc.Settings()
    settings.batches = 10
    settings.particles = 10000
    settings.inactive = 0
    settings.run_mode = "fixed source"
    settings.source = my_source

    # adds a tally to record the heat deposited in entire geometry
    cell_tally = openmc.Tally(name="heating")
    cell_tally.scores = ["heating"]

    # creates a mesh that covers the geometry
    mesh = openmc.RegularMesh()
    mesh.dimension = [100, 100, 100]
    mesh.lower_left = dag_univ.bounding_box[0]
    mesh.upper_right = dag_univ.bounding_box[1]

    # makes a mesh tally using the previously created mesh and records heating on the mesh
    mesh_tally = openmc.Tally(name="heating_on_mesh")
    mesh_filter = openmc.MeshFilter(mesh)
    mesh_tally.filters = [mesh_filter]
    mesh_tally.scores = ["heating"]

    # groups the two tallies
    tallies = openmc.Tallies([cell_tally, mesh_tally])

    # builds the openmc model
    my_model = openmc.Model(
        materials=materials, geometry=geometry, settings=settings, tallies=tallies
    )

    # starts the simulation
    output_file = my_model.run()

    # loads up the output file from the simulation
    statepoint = openmc.StatePoint(output_file)

    # extracts the mesh tally by name
    my_heating_tally = statepoint.get_tally(name="heating_on_mesh")

    mesh.write_data_to_vtk(
        filename="heating_on_mesh.vtk",
        datasets={
            "mean": my_heating_tally.mean
        },  # the first "mean" is the name of the data set label inside the vtk file
    )

    my_heating_cell_tally = statepoint.get_tally(name="heating")
    return my_heating_cell_tally.mean.flatten()[0]


def test_transport_on_h5m_with_6_volumes():

    brep_filename = "tests/test_brep_file.brep"
    h5m_filename = "test_brep_file.h5m"
    volumes = 6
    material_tags = [f"material_{n}" for n in range(1, volumes + 1)]

    brep_to_h5m(
        brep_filename=brep_filename,
        material_tags=material_tags,
        h5m_filename=h5m_filename,
        min_mesh_size=30,
        max_mesh_size=50,
        mesh_algorithm=1,
    )

    transport_particles_on_h5m_geometry(
        h5m_filename=h5m_filename, material_tags=material_tags
    )


def test_transport_on_h5m_with_1_volumes():

    brep_filename = "tests/one_cube.brep"
    h5m_filename = "one_cube.h5m"
    volumes = 1
    material_tags = [f"material_{n}" for n in range(1, volumes + 1)]

    brep_to_h5m(
        brep_filename=brep_filename,
        material_tags=material_tags,
        h5m_filename=h5m_filename,
        min_mesh_size=30,
        max_mesh_size=50,
        mesh_algorithm=1,
    )

    transport_particles_on_h5m_geometry(
        h5m_filename=h5m_filename, material_tags=material_tags
    )


def test_transport_on_h5m_with_2_joined_volumes():

    brep_filename = "tests/test_two_joined_cubes.brep"
    h5m_filename = "test_two_joined_cubes.h5m"
    volumes = 2
    material_tags = [f"material_{n}" for n in range(1, volumes + 1)]

    brep_to_h5m(
        brep_filename=brep_filename,
        material_tags=material_tags,
        h5m_filename=h5m_filename,
        min_mesh_size=30,
        max_mesh_size=50,
        mesh_algorithm=1,
    )

    transport_particles_on_h5m_geometry(
        h5m_filename=h5m_filename, material_tags=material_tags
    )


def test_transport_on_h5m_with_2_sep_volumes():

    brep_filename = "tests/test_two_sep_cubes.brep"
    h5m_filename = "test_two_sep_cubes.h5m"
    volumes = 2
    material_tags = [f"material_{n}" for n in range(1, volumes + 1)]

    brep_to_h5m(
        brep_filename=brep_filename,
        material_tags=material_tags,
        h5m_filename=h5m_filename,
        min_mesh_size=30,
        max_mesh_size=50,
        mesh_algorithm=1,
    )

    transport_particles_on_h5m_geometry(
        h5m_filename=h5m_filename, material_tags=material_tags
    )


def test_transport_result_h5m_with_2_sep_volumes():

    brep_filename = "tests/test_two_sep_cubes.brep"
    h5m_filename = "test_two_sep_cubes.h5m"
    volumes = 2
    material_tags = [f"material_{n}" for n in range(1, volumes + 1)]

    brep_to_h5m(
        brep_filename=brep_filename,
        material_tags=material_tags,
        h5m_filename=h5m_filename,
        min_mesh_size=30,
        max_mesh_size=50,
        mesh_algorithm=1,
    )

    material_tags = list({n: f"material_{n}" for n in range(1, 6 + 1)}.values())
    new_tally = transport_particles_on_h5m_geometry(
        h5m_filename=h5m_filename, material_tags=material_tags
    )

    brep_to_h5m(
        brep_filename=brep_filename,
        material_tags=material_tags,
        h5m_filename=h5m_filename,
        min_mesh_size=30,
        max_mesh_size=50,
        mesh_algorithm=1,
    )
    stl_tally = transport_particles_on_h5m_geometry(
        h5m_filename=h5m_filename, material_tags=material_tags
    )

    assert math.isclose(new_tally, stl_tally)
