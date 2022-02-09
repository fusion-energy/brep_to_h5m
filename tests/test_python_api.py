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

    # TODO add tests to check 7 or more keys results in a value error
    # TODO add tests to mesh sizes impact file size
