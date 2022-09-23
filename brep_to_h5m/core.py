import os
import tempfile
import warnings

import gmsh
import trimesh
from pathlib import Path
from stl_to_h5m import stl_to_h5m
from vertices_to_h5m import vertices_to_h5m
from typing import Tuple, Iterable


def brep_to_h5m(
    brep_filename: str,
    material_tags: Iterable[str],
    h5m_filename: str = "dagmc.h5m",
    min_mesh_size: float = 30,
    max_mesh_size: float = 10,
    mesh_algorithm: int = 1,
) -> str:
    """Converts a Brep file into a DAGMC h5m file. This makes use of Gmsh and
    will therefore need to have Gmsh installed to work.

    Args:
        brep_filename: the filename of the Brep file to convert
        material_tags: A list of material tags to tag the DAGMC volumes with.
            Should be in the same order as the volumes
        h5m_filename: the filename of the DAGMC h5m file to write
        min_mesh_size: the minimum mesh element size to use in Gmsh. Passed
            into gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
        max_mesh_size: the maximum mesh element size to use in Gmsh. Passed
            into gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)
        mesh_algorithm: The Gmsh mesh algorithm number to use. Passed into
            gmsh.option.setNumber("Mesh.Algorithm", mesh_algorithm)
    Returns:
        The filename of the h5m file produced
    """

    gmsh, volumes = mesh_brep(
        brep_filename=brep_filename,
        min_mesh_size=min_mesh_size,
        max_mesh_size=max_mesh_size,
        mesh_algorithm=mesh_algorithm,
    )

    h5m_filename = mesh_to_h5m_in_memory_method(
        volumes=volumes,
        material_tags=material_tags,
        h5m_filename=h5m_filename,
    )

    return h5m_filename


def mesh_brep(
    brep_filename: str,
    min_mesh_size: float = 30,
    max_mesh_size: float = 10,
    mesh_algorithm: int = 1,
):
    """Creates a conformal surface meshes of the volumes in a Brep file using
    Gmsh.

    Args:
        brep_filename: the filename of the Brep file to convert
        min_mesh_size: the minimum mesh element size to use in Gmsh. Passed
            into gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
        max_mesh_size: the maximum mesh element size to use in Gmsh. Passed
            into gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)
        mesh_algorithm: The Gmsh mesh algorithm number to use. Passed into
            gmsh.option.setNumber("Mesh.Algorithm", mesh_algorithm)

    Returns:
        The gmsh object and volumes in Brep file
    """

    if not Path(brep_filename).is_file():
        msg = f"The specified brep ({brep_filename}) file was not found"
        raise FileNotFoundError(msg)

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("made_with_brep_to_h5m_package")
    volumes = gmsh.model.occ.importShapes(brep_filename)
    gmsh.model.occ.synchronize()

    gmsh.option.setNumber("Mesh.Algorithm", mesh_algorithm)
    gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
    gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)
    gmsh.model.mesh.generate(2)

    return gmsh, volumes


def mesh_to_h5m_in_memory_method(
    volumes,
    material_tags: Iterable[str],
    h5m_filename: str = "dagmc.h5m",
) -> str:
    """Converts gmsh volumes into a DAGMC h5m file.

    Args:
        volumes: the volumes in the gmsh file, found with gmsh.model.occ.importShapes
        material_tags: A list of material tags to tag the DAGMC volumes with.
            Should be in the same order as the volumes
        h5m_filename: the filename of the DAGMC h5m file to write

    Returns:
        The filename of the h5m file produced
    """

    if isinstance(material_tags, str):
        msg = f"material_tags should be a list of strings, not a single string."
        raise ValueError(msg)

    if len(volumes) != len(material_tags):
        msg = f"{len(volumes)} volumes found in Brep file is not equal to the number of material_tags {len(material_tags)} provided."
        raise ValueError(msg)

    n = 3  # number of verts in a triangles
    nodes_in_each_pg = []
    for dim_and_vol in volumes:

        # removes all groups so that the following getEntitiesForPhysicalGroup
        # command only finds surfaces for the volume
        gmsh.model.removePhysicalGroups()

        vol_id = dim_and_vol[1]
        entities_in_volume = gmsh.model.getAdjacencies(3, vol_id)
        surfaces_in_volume = entities_in_volume[1]
        ps = gmsh.model.addPhysicalGroup(2, surfaces_in_volume)
        gmsh.model.setPhysicalName(2, ps, f"surfaces_on_volume_{vol_id}")

        groups = gmsh.model.getPhysicalGroups()
        group = groups[0]
        # for group in groups:
        dim = group[0]
        tag = group[1]

        surfaces = gmsh.model.getEntitiesForPhysicalGroup(dim, tag)

        nodes_in_all_surfaces = []
        for surface in surfaces:
            _, _, nodeTags = gmsh.model.mesh.getElements(2, surface)
            nodeTags = nodeTags[0].tolist()
            shifted_node_tags = []
            for nodeTag in nodeTags:
                shifted_node_tags.append(nodeTag - 1)
            grouped_node_tags = [
                shifted_node_tags[i : i + n]
                for i in range(0, len(shifted_node_tags), n)
            ]
            nodes_in_all_surfaces += grouped_node_tags
        nodes_in_each_pg.append(nodes_in_all_surfaces)

    _, all_coords, _ = gmsh.model.mesh.getNodes()

    GroupedCoords = [
        all_coords[i : i + n].tolist() for i in range(0, len(all_coords), n)
    ]

    gmsh.finalize()

    # checks and fixes triangle fix_normals within vertices_to_h5m
    vertices_to_h5m(
        vertices=GroupedCoords,
        triangles=nodes_in_each_pg,
        material_tags=material_tags,
        h5m_filename=h5m_filename,
    )

    return h5m_filename


def mesh_to_h5m_stl_method(
    volumes,
    material_tags: Iterable[str],
    h5m_filename: str = "dagmc.h5m",
    write_stl_files_to_temp: bool = True,
    delete_intermediate_stl_files: bool = True,
) -> str:
    """Converts gmsh volumes into a DAGMC h5m file.

    Args:
        volumes: the volumes in the gmsh file, found with gmsh.model.occ.importShapes
        material_tags: A list of material tags to tag the DAGMC volumes with.
            Should be in the same order as the volumes
        h5m_filename: the filename of the DAGMC h5m file to write
        write_stl_files_to_temp: If set to True the intermediate STL files
            required will be written to the operating systems temporary file
            folder. If set to False the STL files will be written to the
            current working directory.
        delete_intermediate_stl_files: If set to True the intermediate STL
            files produced will be deleted. If set the False the intermediate
            STL files will be left intact.

    Returns:
        The filename of the h5m file produced
    """

    stl_filenames = []
    for dim_and_vol in volumes:
        vol_id = dim_and_vol[1]
        entities_in_volume = gmsh.model.getAdjacencies(3, vol_id)
        surfaces_in_volume = entities_in_volume[1]
        ps = gmsh.model.addPhysicalGroup(2, surfaces_in_volume)
        gmsh.model.setPhysicalName(2, ps, f"surfaces_on_volume_{vol_id}")
        if write_stl_files_to_temp:
            tmp_filename = tempfile.mkstemp(suffix=".stl", prefix=f"volume_{vol_id}")[1]
        else:
            tmp_filename = f"volume_{vol_id}.stl"
        gmsh.write(tmp_filename)
        stl_filenames.append((vol_id, tmp_filename))
        gmsh.model.removePhysicalGroups([])  # removes all groups
    gmsh.finalize()

    files_with_tags = []
    for filename_vol_id in stl_filenames:
        filename = filename_vol_id[1]
        vol_id = filename_vol_id[0]
        # if vol_id in volumes_with_tags.keys():
        mesh = trimesh.load_mesh(filename, file_type="stl")
        if mesh.is_watertight is False:
            msg = f"file {filename} is watertight"
            warnings.warn(msg)
        trimesh.repair.fix_normals(
            mesh
        )  # reqired as gmsh stl export from brep can get the inside outside mixed up
        new_filename = filename[:-4] + "_with_corrected_face_normals.stl"
        mesh.export(new_filename)

        if delete_intermediate_stl_files:
            os.remove(filename)  # deletes tmp stl file
        tag_name = material_tags[vol_id - 1]
        if not tag_name.startswith("mat:"):
            # TODO check if graveyard or mat_graveyard should be excluded
            # and tag_name.lower!='graveyard':
            tag_name = f"mat:{tag_name}"
        files_with_tags.append((new_filename, tag_name))

    stl_to_h5m(files_with_tags=files_with_tags, h5m_filename=h5m_filename)

    # deletes the stl with corrected faces file from the tmp dir
    if delete_intermediate_stl_files:
        for file_to_del in files_with_tags:
            os.remove(file_to_del[0])

    return h5m_filename


def transport_particles_on_h5m_geometry(
    h5m_filename: str,
    material_tags: list,
    nuclides: list = None,
    cross_sections_xml: str = None,
):
    """A function for testing the geometry file with particle transport in
    DAGMC OpenMC. Requires openmc and either the cross_sections_xml to be
    specified or openmc_data_downloader installed. Returns the flux on each
    volume

    Arg:
        h5m_filename: The name of the DAGMC h5m file to test
        material_tags: The
        nuclides:
        cross_sections_xml:

    """

    import openmc
    from openmc.data import NATURAL_ABUNDANCE

    if nuclides is None:
        nuclides = list(NATURAL_ABUNDANCE.keys())

    materials = openmc.Materials()
    for i, material_tag in enumerate(material_tags):

        # simplified material definitions have been used to keen this example minimal
        mat_dag_material_tag = openmc.Material(name=material_tag)
        mat_dag_material_tag.add_nuclide(nuclides[i], 1, "ao")
        mat_dag_material_tag.set_density("g/cm3", 0.1)

        materials.append(mat_dag_material_tag)

    if cross_sections_xml:
        materials.cross_sections = cross_sections_xml
    else:
        # downloads the nuclear data and sets the openmc_cross_sections environmental variable
        import openmc_data_downloader as odd

        odd.just_in_time_library_generator(
            libraries="ENDFB-7.1-NNDC", materials=materials
        )

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
    cell_tally = openmc.Tally(name="flux")
    cell_tally.scores = ["flux"]

    # groups the two tallies
    tallies = openmc.Tallies([cell_tally])

    # builds the openmc model
    my_model = openmc.Model(
        materials=materials, geometry=geometry, settings=settings, tallies=tallies
    )

    # starts the simulation
    output_file = my_model.run()

    # loads up the output file from the simulation
    statepoint = openmc.StatePoint(output_file)

    my_flux_cell_tally = statepoint.get_tally(name="flux")

    return my_flux_cell_tally.mean.flatten()[0]
