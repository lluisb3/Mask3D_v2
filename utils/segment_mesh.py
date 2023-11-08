import meshlib.mrmeshpy as mrmeshpy
import meshlib.mrmeshnumpy as mrmeshnumpy
from plyfile import PlyData
from pathlib import Path

thispath = Path(__file__).resolve()

def test_segmentation(mesh):
    metric = mrmeshpy.edgeLengthMetric(mesh)
    source = mrmeshpy.FaceBitSet()
    sink = mrmeshpy.FaceBitSet()
    source.resize(mesh.topology.getValidFaces().size(),False)
    sink.resize(mesh.topology.getValidFaces().size(),False)

    source.set(mrmeshpy.FaceId(0),True)
    sink.set(mrmeshpy.FaceId(5),True)

    res = mrmeshpy.segmentByGraphCut(mesh.topology,source,sink,metric)

    assert (res.count() != 0)
    assert (res.test(mrmeshpy.FaceId(0)))
    assert (not res.test(mrmeshpy.FaceId(5)))
    print(res.test)

    return res


def main():
    datapath = f"{thispath.parent.parent}/data/raw/hesso"

    filename = "scene4444_00.ply"

    filepath = f"{datapath}/{filename}"

    mesh = PlyData.read(filepath)

    res = test_segmentation(mesh)

    mesh.addPartByMask(mesh, res)

    mrmeshpy.saveMesh(mesh, f"{datapath}/mesh_seg.ply")

if __name__ == "__main__":
    main()