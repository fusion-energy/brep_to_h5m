import tempfile

import gmsh
import trimesh
from stl_to_h5m import stl_to_h5m


def brep_to_h5m(
    brep_filename: str,
    volumes_with_tags: dict,
    h5m_filename: str = "dagmc.h5m",
    min_mesh_size: int = 30,
    max_mesh_size: int = 10,
    mesh_algorithm: int = 1,
    write_stl_files_to_temp: bool = True,
    delete_intermediate_stl_files: bool = True,
):
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
            required will be written to the opperating systems temporary file
            folder. If set to False the STL files will be written to the
            current working directory.
        delete_intermediate_stl_files: If set to True the intermediate STL
            files produced will be deleted. If set the False the intermediate
            STL files will be left intact.

    """

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("made_with_brep_to_h5m_package")
    volumes = gmsh.model.occ.importShapes(brep_filename)
    gmsh.model.occ.synchronize()

    vols_in_brep = len(volumes)
    vols_provided_by_user = len(volumes_with_tags.keys())

    if vols_in_brep != vols_provided_by_user:
        print(
            f"{vols_in_brep} volumes found in Brep file but only {vols_provided_by_user} volumes provided in volumes_with_tags argument."
        )

    if vols_in_brep < vols_provided_by_user:
        msg = f"The Brep file contains {vols_in_brep} volumes but {vols_provided_by_user} volumes are provided in the volumes_with_tags argument. Please reduce the number of volumes in volumes_with_tags"
        raise ValueError(msg)

    gmsh.option.setNumber("Mesh.Algorithm", mesh_algorithm)
    gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
    gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)
    gmsh.model.mesh.generate(2)
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
            mesh = trimesh.load_mesh(filename)
            print("file", filename, "is watertight", mesh.is_watertight)
            trimesh.repair.fix_normals(
                mesh
            )  # reqired as gmsh stl export from brep can get the inside outside mixed up
            new_filename = filename[:-4] + "_with_corrected_face_normals.stl"
            mesh.export(new_filename)
            import os

            if delete_intermediate_stl_files:
                os.remove(filename)  # deletes tmp stl file
            tag_name = volumes_with_tags[vol_id]
            if not tag_name.startswith("mat_"):
                # TODO check if graveyard or mat_graveyard should be excluded
                # and tag_name.lower!='graveyard':
                tag_name = "mat_" + tag_name
            files_with_tags.append((new_filename, tag_name))

    stl_to_h5m(files_with_tags=files_with_tags, h5m_filename=h5m_filename)

    # deletes the stl with corrected faces file from the tmp dir
    if delete_intermediate_stl_files:
        for file_to_del in files_with_tags:
            os.remove(file_to_del[0])

    return h5m_filename
