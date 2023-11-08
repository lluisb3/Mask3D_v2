import math
import numpy as np
import json
from plyfile import PlyData
from pathlib import Path

thispath = Path(__file__).resolve()

 
# Felzenswalb segmentation (https://cs.brown.edu/~pff/segment/index.html)
 
# Disjoint-set forests using union-by-rank and path compression (sort of).
class Universe:
    def __init__(self, elements):
        self.elts = [UniElement(i) for i in range(elements)]
        self.num = elements
 
    def find(self, x):
        y = x
        while y != self.elts[y].p:
            y = self.elts[y].p
        self.elts[x].p = y
        return y
 
    def join(self, x, y):
        if self.elts[x].rank > self.elts[y].rank:
            self.elts[y].p = x
            self.elts[x].size += self.elts[y].size
        else:
            self.elts[x].p = y
            self.elts[y].size += self.elts[x].size
            if self.elts[x].rank == self.elts[y].rank:
                self.elts[y].rank += 1
        self.num -= 1
 
    def size(self, x):
        return self.elts[x].size
 
    def num_sets(self):
        return self.num
 
class UniElement:
    def __init__(self, index):
        self.rank = 0
        self.p = index
        self.size = 1
 
class Edge:
    def __init__(self, w, a, b):
        self.w = w
        self.a = a
        self.b = b
 
def segment_graph(num_vertices, num_edges, edges, c):
    edges.sort(key=lambda x: x.w)
    u = Universe(num_vertices)
    threshold = [c] * num_vertices
 
    for i in range(num_edges):
        pedge = edges[i]
        a = u.find(pedge.a)
        b = u.find(pedge.b)
        if a != b:
            if pedge.w <= threshold[a] and pedge.w <= threshold[b]:
                u.join(a, b)
                a = u.find(a)
                threshold[a] = pedge.w + (c / u.size(a))
 
    return u
 
class Vec3f:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
 
    def __add__(self, other):
        return Vec3f(self.x + other.x, self.y + other.y, self.z + other.z)
 
    def __sub__(self, other):
        return Vec3f(self.x - other.x, self.y - other.y, self.z - other.z)
 
def cross(u, v):
    c = Vec3f(u.y * v.z - u.z * v.y, u.z * v.x - u.x * v.z, u.x * v.y - u.y * v.x)
    n = math.sqrt(c.x * c.x + c.y * c.y + c.z * c.z)
    c.x /= n
    c.y /= n
    c.z /= n
    return c
 
def lerp(a, b, v):
    u = 1.0 - v
    return Vec3f(v * b.x + u * a.x, v * b.y + u * a.y, v * b.z + u * a.z)
 
def ends_with(value, ending):
    return value[-len(ending):] == ending
 



# def main(mesh_file, kthr, seg_min_verts):
verts = []
faces = []

datapath = f"{thispath.parent.parent}/data/raw/hesso"

filename = "scene4444_00.ply"

mesh_file = f"{datapath}/{filename}"

if ends_with(mesh_file, ".ply") or ends_with(mesh_file, ".PLY"):
    with open(mesh_file, 'rb') as file:
        # Load the geometry from .ply
        plydata = PlyData.read(file)
        vertexCount = plydata['vertex'].count
        for vertex in plydata['vertex']:
            verts.extend([vertex['x'], vertex['y'], vertex['z']])
        faceCount = plydata['face'].count
        faces = plydata['face']['vertex_indices']
elif ends_with(mesh_file, ".obj") or ends_with(mesh_file, ".OBJ"):
    # Load the geometry from .obj
    # Implement loading from .obj file if needed
    pass

print(f"Read mesh with vertexCount {vertexCount}, verts size {len(verts)}, faceCount {faceCount}, faces size {len(faces)}")

points = [Vec3f() for _ in range(vertexCount)]
normals = [Vec3f() for _ in range(vertexCount)]
counts = [0] * len(verts)
edges_count = faceCount * 3
edges = [Edge(0.0, 0, 0) for _ in range(edges_count)]

for i in range(faceCount):
    fbase = 3 * i
    i1, i2, i3 = faces[fbase[0]], faces[fbase[1]], faces[fbase[2]]
    vbase = 3 * i1
    p1 = Vec3f(verts[vbase[0]], verts[vbase[1]], verts[vbase[2]])
    vbase = 3 * i2
    p2 = Vec3f(verts[vbase[0]], verts[vbase[1]], verts[vbase[2]])
    vbase = 3 * i3
    p3 = Vec3f(verts[vbase[0]], verts[vbase[1]], verts[vbase[2]])
    print(i1)
    points[i1] = p1
    points[i2] = p2
    points[i3] = p3
    ebase = 3 * i
    edges[ebase].a = i1
    edges[ebase].b = i2
    edges[ebase + 1].a = i1
    edges[ebase + 1].b = i3
    edges[ebase + 2].a = i3
    edges[ebase + 2].b = i2

    normal = cross(p2 - p1, p3 - p1)
    normals[i1] = lerp(normals[i1], normal, 1.0 / (counts[i1] + 1.0))
    normals[i2] = lerp(normals[i2], normal, 1.0 / (counts[i2] + 1.0))
    normals[i3] = lerp(normals[i3], normal, 1.0 / (counts[i3] + 1.0))
    counts[i1] += 1
    counts[i2] += 1
    counts[i3] += 1

for i in range(edges_count):
    a, b = edges[i].a, edges[i].b
    n1, n2 = normals[a], normals[b]
    p1, p2 = points[a], points[b]
    dx, dy, dz = p2.x - p1.x, p2.y - p1.y, p2.z - p1.z
    dd = math.sqrt(dx * dx + dy * dy + dz * dz)

# if __name__ == "__main__":
#     main()