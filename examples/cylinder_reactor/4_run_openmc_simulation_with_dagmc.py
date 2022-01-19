# A minimal example that obtains TBR on the blanket and fast neutron flux on all
# cells in the DAGMC geometry.
# Particular emphasis is placed on explaining the openmc-dagmc-wrapper
# extentions of openmc base classes.


import openmc
import openmc_dagmc_wrapper as odw
from openmc_plasma_source import FusionRingSource
from openmc_mesh_tally_to_vtk import write_mesh_tally_to_vtk


h5m_filename = "dagmc.h5m"

# creates a geometry object from a DAGMC geometry.
# In this case the geometry doen't have a graveyard cell.
# So a set of 6 CSG surfaces are automatically made and added to the geometry
geometry = odw.Geometry(h5m_filename=h5m_filename, reflective_angles=(0, 3.14159265359))

# Creates the materials to use in the problem using by linking the material
# tags in the DAGMC h5m file with material definitions in the
# neutronics-material-maker. One could also use openmc.Material or nmm.Material
# objects instead of the strings used here
materials = odw.Materials(
    h5m_filename=h5m_filename,
    correspondence_dict={
        # "material_for_volume_1": "Be", # removed plasma as not many interactions occur here
        "material_for_volume_2": "Be",  # applying beryllium to all materials to reduce nuclear data loading time
        "material_for_volume_3": "Be",
        "material_for_volume_4": "Be",
        "material_for_volume_5": "Be",
        "material_for_volume_6": "Be",
        "material_for_volume_7": "Be",
        "material_for_volume_8": "Be",
    },
)

# makes use of the dagmc-bound-box package to get the corners of the bounding
# box. This will be used to set the bounding box for the tally. This can be
# expanded with the expand keyword if needed
my_bounding_box = geometry.corners()

# A MeshTally3D tally allows a set of standard tally types (made from filters
# and scores) to be applied to the DAGMC geometry. By default the mesh will be
# applied across the entire geomtry with and the size of the geometry is
# automatically found.
tally1 = odw.MeshTally3D(tally_type="flux", bounding_box=my_bounding_box)
tally2 = odw.MeshTally3D(tally_type="heating", bounding_box=my_bounding_box)

# no modifications are made to the default openmc.Tallies
tallies = openmc.Tallies([tally1, tally2])

# Creates and openmc settings object with the run mode set to 'fixed source'
# and the number of inactivate particles set to zero. Setting these to values
# by default means less code is needed by the user and less chance of simulating
# batches that don't contribute to the tallies
settings = odw.FusionSettings()
settings.batches = 1
settings.particles = 100_000
# assigns a ring source of DT energy neutrons to the source using the
# openmc_plasma_source package
settings.source = FusionRingSource(fuel="DT", angles=(0, 3.14159265359), radius=330)

# no modifications are made to the default openmc.Model object
my_model = openmc.Model(
    materials=materials, geometry=geometry, settings=settings, tallies=tallies
)
statepoint_file = my_model.run()

# loads the output statepoint file
statepoint = openmc.StatePoint(statepoint_file)

# assumes the statepoint file has a RegularMesh tally with a certain name
my_tally = statepoint.get_tally(name="flux_on_3D_mesh")

# converts the tally result into a VTK file
write_mesh_tally_to_vtk(
    tally=my_tally,
    filename="flux_on_3D_mesh.vtk",
)
# assumes the statepoint file has a RegularMesh tally with a certain name
my_tally = statepoint.get_tally(name="heating_on_3D_mesh")

# converts the tally result into a VTK file
write_mesh_tally_to_vtk(
    tally=my_tally,
    filename="heating_on_3D_mesh.vtk",
)
