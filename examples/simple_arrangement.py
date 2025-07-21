from discopygal.bindings import *
from discopygal.geometry_utils.display_arrangement import display_arrangement

if __name__ == "__main__":
    # Create a "triangle" with rounded corners
    polygon = Polygon_2([Point_2(0, 0), Point_2(0, 1), Point_2(1, 0)])
    ms = Ms2.approximated_offset_2(polygon, FT(0.4), 0.01)

    # Insert outer & hole curves to an arrangement
    arr = Arrangement_2()
    curves_iter = ms.outer_boundary().curves()
    curves = list([curve for curve in curves_iter])
    Aos2.insert(arr, curves)
    for hole in ms.holes():
        holes_iter = hole.curves()
        holes = [curve for curve in holes_iter]
        Aos2.insert(arr, holes)


    ubf = arr.unbounded_face()
    ubf.set_data(1)

    # Color the (rounded) triangle face as "invalid"
    invalid_face = next(next(ubf.inner_ccbs())).twin().face()
    invalid_face.set_data(-1)


    display_arrangement(arr, init_qt=True)