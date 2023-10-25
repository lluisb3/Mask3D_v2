from pathlib import Path
import shutil


thispath = Path(__file__).resolve()

datadir = Path(thispath.parent.parent / "data" / "raw" / "scannet_dataset" / "scans_test")

outputdir = Path(thispath.parent.parent / "data" / "raw" / "scannet_test_segments")
outputdir.mkdir(exist_ok=True, parents=True)

json_test_files = [i for i in datadir.rglob("*.segs.json")]

for file in json_test_files:
    shutil.copy(file, outputdir / f"{file.stem}{file.suffixes[-1]}")
