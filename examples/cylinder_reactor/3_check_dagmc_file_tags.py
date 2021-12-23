import dagmc_h5m_file_inspector as di

tags = di.get_volumes_and_materials_from_h5m("dagmc.h5m")

print(tags)
