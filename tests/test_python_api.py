import os
from pathlib import Path

from brep_to_h5m import brep_to_h5m


class TestApiUsage:
    """Test usage cases"""

    def test_h5m_file_creation(self):
        """Checks that a h5m file is created from a brep file"""

        os.system("rm test_brep_file.h5m")
        brep_to_h5m(
            brep_filename="tests/test_brep_file.brep",
            volumes_with_tags={
                1: "material_for_volume_1",
                2: "material_for_volume_2",
                3: "material_for_volume_3",
                4: "material_for_volume_4",
                5: "material_for_volume_5",
                6: "material_for_volume_6",
            },
            h5m_filename="test_brep_file.h5m",
            min_mesh_size=30,
            max_mesh_size=50,
            mesh_algorithm=1,
        )

        assert Path("test_brep_file.h5m").is_file()

    def test_max_mesh_size_impacts_file_size(self):
        """Checks the reducing max_mesh_size value increases the file size"""

        os.system("rm *.h5m")
        brep_to_h5m(
            brep_filename="tests/test_brep_file.brep",
            volumes_with_tags={
                1: "material_for_volume_1",
                2: "material_for_volume_2",
                3: "material_for_volume_3",
                4: "material_for_volume_4",
                5: "material_for_volume_5",
                6: "material_for_volume_6",
            },
            h5m_filename="test_brep_file_10.h5m",
            min_mesh_size=20,
            max_mesh_size=19,
            mesh_algorithm=1,
        )
        brep_to_h5m(
            brep_filename="tests/test_brep_file.brep",
            volumes_with_tags={
                1: "material_for_volume_1",
                2: "material_for_volume_2",
                3: "material_for_volume_3",
                4: "material_for_volume_4",
                5: "material_for_volume_5",
                6: "material_for_volume_6",
            },
            h5m_filename="test_brep_file_30.h5m",
            min_mesh_size=20,
            max_mesh_size=30,
            mesh_algorithm=1,
        )

        assert Path("test_brep_file_10.h5m").is_file()
        assert Path("test_brep_file_30.h5m").is_file()

        large_file = Path("test_brep_file_10.h5m").stat().st_size
        small_file = Path("test_brep_file_30.h5m").stat().st_size
        assert small_file < large_file

    # TODO add tests to check 7 or more keys results in a value error
