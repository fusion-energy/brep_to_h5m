import os
import tempfile
import warnings

import gmsh
import trimesh
from pathlib import Path
from stl_to_h5m import stl_to_h5m
from vertices_to_h5m import vertices_to_h5m


def brep_to_h5m(
    brep_filename: str,
    volumes_with_tags: dict,
    h5m_filename: str = "dagmc.h5m",
    min_mesh_size: int = 30,
    max_mesh_size: int = 10,
    mesh_algorithm: int = 1,
    write_stl_files_to_temp: bool = True,
    delete_intermediate_stl_files: bool = True,
    method="stl",
) -> str:
    """Converts a Brep file into a DAGMC h5m file. This makes use of Gmsh and
    will therefore need to have Gmsh installed to work.

    Args:
        brep_filename: the filename of the Brep file to convert
        volumes_with_tags: a dictionary with volume numbers as the keys and
            the tag names to use in DAGMC as te values.
        h5m_filename: the filename of the DAGMC h5m file to write
        min_mesh_size: the minimum mesh element size to use in Gmsh. Passed
            into gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
        max_mesh_size: the maximum mesh element size to use in Gmsh. Passed
            into gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)
        mesh_algorithm: The Gmsh mesh algorithm number to use. Passed into
            gmsh.option.setNumber("Mesh.Algorithm", mesh_algorithm)
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

    gmsh, volumes = mesh_brep(
        brep_filename=brep_filename,
        min_mesh_size=min_mesh_size,
        max_mesh_size=max_mesh_size,
        mesh_algorithm=mesh_algorithm,
        volumes_with_tags=volumes_with_tags,
    )
    if method == "stl":
        h5m_filename = mesh_to_h5m_stl_method(
            volumes=volumes,
            volumes_with_tags=volumes_with_tags,
            h5m_filename=h5m_filename,
            write_stl_files_to_temp=write_stl_files_to_temp,
            delete_intermediate_stl_files=delete_intermediate_stl_files,
        )
    else:
        h5m_filename = mesh_to_h5m_in_memory_method(
            volumes=volumes,
            volumes_with_tags=volumes_with_tags,
            h5m_filename=h5m_filename,
        )

    return h5m_filename


def mesh_brep(
    brep_filename: str,
    volumes_with_tags: dict,
    min_mesh_size: int = 30,
    max_mesh_size: int = 10,
    mesh_algorithm: int = 1,
):
    """Converts a Brep file into a DAGMC h5m file. This makes use of Gmsh and
    will therefore need to have Gmsh installed to work.

    Args:
        brep_filename: the filename of the Brep file to convert
        volumes_with_tags: a dictionary with volume numbers as the keys and
            the tag names to use in DAGMC as te values.
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
        raise FileNotFoundError()

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("made_with_brep_to_h5m_package")
    volumes = gmsh.model.occ.importShapes(brep_filename)
    gmsh.model.occ.synchronize()

    vols_in_brep = len(volumes)
    vols_provided_by_user = len(volumes_with_tags.keys())

    if vols_in_brep != vols_provided_by_user:
        msg = f"{vols_in_brep} volumes found in Brep file but only {vols_provided_by_user} volumes provided in volumes_with_tags argument."
        warnings.warn(msg)

    if vols_in_brep < vols_provided_by_user:
        msg = f"The Brep file contains {vols_in_brep} volumes but {vols_provided_by_user} volumes are provided in the volumes_with_tags argument. Please reduce the number of volumes in volumes_with_tags"
        raise ValueError(msg)

    gmsh.option.setNumber("Mesh.Algorithm", mesh_algorithm)
    gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
    gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)
    gmsh.model.mesh.generate(2)

    return gmsh, volumes


def mesh_to_h5m_in_memory_method(
    volumes,
    volumes_with_tags,
    h5m_filename: str = "dagmc.h5m",
) -> str:

    print("volumes_with_tags", volumes_with_tags)

    material_tags = []
    for tag_name in volumes_with_tags.values():
        # caused error in transport
        # ERROR: No material 'mat' found for volume (cell) 1
        # if not tag_name.startswith("mat:"):
        #     tag_name = f"mat:{tag_name}"
        material_tags.append(tag_name)
    print("material_tags", material_tags)

    all_coords = []
    n = 3

    for dim_and_vol in volumes:
        vol_id = dim_and_vol[1]
        print("vol_id", vol_id)
        entities_in_volume = gmsh.model.getAdjacencies(3, vol_id)
        surfaces_in_volume = entities_in_volume[1]
        ps = gmsh.model.addPhysicalGroup(2, surfaces_in_volume)
        print("surfaces_in_volume", surfaces_in_volume)
        gmsh.model.setPhysicalName(2, ps, f"surfaces_on_volume_{vol_id}")

    gmsh.model.mesh.generate(2)

    nodes_in_each_pg = []
    groups = gmsh.model.getPhysicalGroups()
    for group in groups:
        dim = group[0]
        tag = group[1]

        surfaces = gmsh.model.getEntitiesForPhysicalGroup(dim, tag)

        nodes_in_all_surfaces = []
        for surface in surfaces:
            elementTypes, elementTags, nodeTags = gmsh.model.mesh.getElements(
                2, surface
            )
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

    all_nodes, all_coords, _ = gmsh.model.mesh.getNodes()

    GroupedCoords = [
        all_coords[i : i + n].tolist() for i in range(0, len(all_coords), n)
    ]

    gmsh.finalize()

    print("material_tags", material_tags)

    vertices_to_h5m(
        vertices=GroupedCoords,
        triangles=nodes_in_each_pg,
        material_tags=material_tags,
        h5m_filename=h5m_filename,
    )

    return h5m_filename


def mesh_to_h5m_stl_method(
    volumes,
    volumes_with_tags,
    h5m_filename: str = "dagmc.h5m",
    write_stl_files_to_temp: bool = True,
    delete_intermediate_stl_files: bool = True,
) -> str:
    """Converts a Brep file into a DAGMC h5m file. This makes use of Gmsh and
    will therefore need to have Gmsh installed to work.

    Args:
        mesh: the gmsh mesh object
        volumes: the volumes in the gmsh file, found with gmsh.model.occ.importShapes
        h5m_filename: the filename of the DAGMC h5m file to write
        write_stl_files_to_temp: If set to True the intermediate STL files
            required will be written to the operating systems temporary file
            folder. If set to False the STL files will be written to the
            current working directory.
        delete_intermediate_stl_files: If set to True the intermediate STL
            files produced will be deleted. If set the False the intermediate
            STL files will be left intact.
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
        if vol_id in volumes_with_tags.keys():
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
            tag_name = volumes_with_tags[vol_id]
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
