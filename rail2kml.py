#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import math
import os

import shapefile
import simplekml


class PathSearchError(Exception):
    pass


def relpath_to_abspath(rel_path):
    abs_path = os.path.join(os.path.dirname(__file__), rel_path)
    return abs_path


def read_shapefile(path, is_abs):
    if is_abs is False:
        rail_abspath = relpath_to_abspath(path["rail"])
        station_abspath = relpath_to_abspath(path["station"])
    else:
        rail_abspath = path["rail"]
        station_abspath = path["station"]
    shape_recs = {}
    shape_recs.update(
        {
            "rail": shapefile.Reader(
                rail_abspath, encoding="shift_jis"
            ).shapeRecords()
        }
    )
    shape_recs.update(
        {
            "station": shapefile.Reader(
                station_abspath, encoding="shift_jis"
            ).shapeRecords()
        }
    )
    return shape_recs


def get_stations_edges(section, shape_recs_station):
    stations_edges = dict({"start": set(), "goal": set(), "others": set()})
    for shape_rec_station in shape_recs_station:
        line_name = shape_rec_station.record[2]
        company_name = shape_rec_station.record[3]
        station_name = shape_rec_station.record[4]
        if line_name == section["line"] and company_name == section["company"]:
            if station_name == section["start"]:
                stations_edges["start"].add(
                    tuple(shape_rec_station.shape.points)
                )
            elif station_name == section["goal"]:
                stations_edges["goal"].add(
                    tuple(shape_rec_station.shape.points)
                )
            else:
                stations_edges["others"].add(
                    tuple(
                        [
                            shape_rec_station.record[4],
                            tuple(shape_rec_station.shape.points),
                        ]
                    )
                )
        else:
            pass
    if len(stations_edges["start"]) == 0:
        err_msg = (
            "Station is not found."
            + "（"
            + section["company"]
            + "_"
            + section["line"]
            + "_"
            + section["start"]
            + "）"
        )
        raise PathSearchError(err_msg)
    elif len(stations_edges["goal"]) == 0:
        err_msg = (
            "Station is not found."
            + "("
            + section["company"]
            + "_"
            + section["line"]
            + "_"
            + section["goal"]
            + ")"
        )
        raise PathSearchError(err_msg)
    else:
        pass
    return stations_edges


def get_line_edges(line_name, company_name, shape_recs_rail, patch):
    line_edges = set()
    for shape_rec_rail in shape_recs_rail:
        if (
            line_name == shape_rec_rail.record[2]
            and company_name == shape_rec_rail.record[3]
        ):
            line_edges.add(tuple(shape_rec_rail.shape.points))
    for patch_each in patch:
        if line_name == patch_each[0] and company_name == patch_each[1]:
            line_edges.add(tuple(patch_each[2]))
    return line_edges


def is_equal_coordinate(target, base):
    EQUAL_RANGE = 0.00001
    if (
        (base[0] - EQUAL_RANGE < target[0])
        and (target[0] < base[0] + EQUAL_RANGE)
    ) and (
        (base[1] - EQUAL_RANGE < target[1])
        and (target[1] < base[1] + EQUAL_RANGE)
    ):
        is_equal = True
    else:
        is_equal = False

    return is_equal


def is_equal_edge(target, base):
    if len(target) == len(base):
        is_equal = True
        for target_coordinate, base_coordinate in zip(target, base):
            if is_equal_coordinate(target_coordinate, base_coordinate):
                pass
            else:
                is_equal = False
                break
    else:
        is_equal = False

    return is_equal


def is_equal_edge_both_directions(target, base):
    if is_equal_edge(target, base) or is_equal_edge(
        tuple(reversed(target)), base
    ):
        is_equal = True
    else:
        is_equal = False

    return is_equal


def is_included_in_edges(target, edges):
    is_included = False
    for edge in edges:
        if is_equal_edge(target, edge):
            is_included = True
            break
        else:
            pass

    return is_included


def is_included_in_edges_both_directions(target, edges):
    if is_included_in_edges(target, edges) or is_included_in_edges(
        tuple(reversed(target)), edges
    ):
        is_included = True
    else:
        is_included = False

    return is_included


def get_equal_edge_from_edges_both_directions(target, edges):
    equal_edge = None
    for edge in edges:
        if is_equal_edge(target, edge) or is_equal_edge(
            tuple(reversed(target)), edge
        ):
            equal_edge = edge
            break

    return equal_edge


def path_search(station_edges, line_edges):
    def path_search_innner(start_point, passed_edges, before_passed_edge):
        nonlocal section_edges, unreachable_edges, station_edges, line_edges
        is_unreachable = 1
        is_by_passed = 0
        for line_edge in line_edges:
            if (
                is_equal_coordinate(line_edge[0], start_point)
                and line_edge not in passed_edges
            ):
                is_unreachable = 0
                if line_edge in section_edges:
                    section_edges |= passed_edges
                elif line_edge not in unreachable_edges:
                    if is_equal_edge_both_directions(
                        line_edge, station_edges["goal"]
                    ):
                        section_edges |= passed_edges | set([line_edge])
                    else:
                        path_search_innner(
                            line_edge[-1],
                            passed_edges | set([line_edge]),
                            line_edge,
                        )
                else:
                    pass
            elif (
                is_equal_coordinate(line_edge[-1], start_point)
                and line_edge not in passed_edges
            ):
                is_unreachable = 0
                if line_edge in section_edges:
                    section_edges |= passed_edges
                elif line_edge not in unreachable_edges:
                    if is_equal_edge_both_directions(
                        line_edge, station_edges["goal"]
                    ):
                        section_edges |= passed_edges | set([line_edge])
                    else:
                        path_search_innner(
                            line_edge[0],
                            passed_edges | set([line_edge]),
                            line_edge,
                        )
                else:
                    pass
            elif (
                is_equal_coordinate(line_edge[0], start_point)
                or is_equal_coordinate(line_edge[-1], start_point)
            ) and line_edge != before_passed_edge:
                is_by_passed = 1
            else:
                pass
        if is_unreachable == 1 and is_by_passed == 0:
            unreachable_edges |= passed_edges
        else:
            pass

    start_station_edge_in_line = get_equal_edge_from_edges_both_directions(
        station_edges["start"], line_edges
    )
    section_edges = set()
    unreachable_edges = set()
    if start_station_edge_in_line is not None:
        path_search_innner(
            start_station_edge_in_line[-1],
            set([start_station_edge_in_line]),
            start_station_edge_in_line,
        )
    section_edges_forward = section_edges

    section_edges = set()
    unreachable_edges = set()
    if start_station_edge_in_line is not None:
        path_search_innner(
            start_station_edge_in_line[0],
            set([start_station_edge_in_line]),
            start_station_edge_in_line,
        )
    section_edges_reverse = section_edges

    if len(section_edges_forward) != 0 and len(section_edges_reverse) != 0:
        if len(section_edges_forward) <= len(section_edges_reverse):
            section_edges = section_edges_forward
        else:
            section_edges = section_edges_reverse
    elif len(section_edges_forward) != 0:
        section_edges = section_edges_forward
    else:
        section_edges = section_edges_reverse

    return section_edges


def get_middle_stations(section_edges, stations_edges):
    middle_station_edges = set()
    for other_station_edges in stations_edges["others"]:
        if is_included_in_edges_both_directions(
            other_station_edges[1], section_edges
        ):
            middle_station_edges.add(other_station_edges)
        else:
            pass
    stations_edges.update({"middle": middle_station_edges})
    del stations_edges["others"]
    return stations_edges


def get_section_edges(section, shape_recs, patch):
    line_edges = get_line_edges(
        section["line"], section["company"], shape_recs["rail"], patch
    )
    stations_edges = get_stations_edges(section, shape_recs["station"])
    section_edges = set()
    unused_station_edges = dict(
        {
            "start": set(stations_edges["start"]),
            "goal": set(stations_edges["goal"]),
        }
    )
    for start_station_edges in stations_edges["start"]:
        for goal_station_edges in stations_edges["goal"]:
            station_edges = dict(
                {"start": start_station_edges, "goal": goal_station_edges}
            )
            section_edges_each = path_search(station_edges, line_edges)
            section_edges |= section_edges_each
            if len(section_edges_each) == 0:
                pass
            else:
                unused_station_edges["start"].discard(start_station_edges)
                unused_station_edges["goal"].discard(goal_station_edges)
    stations_edges["start"] -= unused_station_edges["start"]
    stations_edges["goal"] -= unused_station_edges["goal"]
    if len(section_edges) == 0:
        err_msg = "Path not found."
        raise PathSearchError(err_msg)
    else:
        pass
    stations_edges = get_middle_stations(section_edges, stations_edges)
    return (section_edges, stations_edges)


def get_center_station_point(station_edge):
    section_length = list()
    for i in range(len(station_edge) - 1):
        section_length.append(
            math.sqrt(
                (station_edge[i][0] - station_edge[i + 1][0]) ** 2
                + (station_edge[i][1] - station_edge[i + 1][1]) ** 2
            )
        )
    sum_length = sum(section_length)
    added_length = 0
    for i, add_length in enumerate(section_length):
        if add_length > (sum_length / 2) - added_length:
            break
        added_length += add_length
    center_ratio = ((sum_length / 2) - added_length) / add_length
    center_station_point = tuple(
        [
            (
                station_edge[i][0] * (1 - center_ratio)
                + station_edge[i + 1][0] * center_ratio
            ),
            (
                station_edge[i][1] * (1 - center_ratio)
                + station_edge[i + 1][1] * center_ratio
            ),
        ]
    )
    return center_station_point


def output_kml(
    section_edges_list,
    stations_edges_list,
    section_list,
    is_including_middles,
    SAVE_PATH,
    is_abs,
):
    kml_name = ""
    for section in section_list:
        kml_name += (
            section["company"]
            + "_"
            + section["line"]
            + "（"
            + section["start"]
            + "－"
            + section["goal"]
            + "）"
            + "、"
        )
    kml_name = kml_name[:-1]
    kml = simplekml.Kml(name=kml_name)
    edges2kml = set()
    for section_edges in section_edges_list:
        for section_edge in section_edges:
            edges2kml.add(section_edge)
    for edge2kml in edges2kml:
        ls = kml.newlinestring()
        ls.coords = list(edge2kml)
        ls.extrude = 1
        ls.altitudemode = simplekml.AltitudeMode.relativetoground
        ls.style.linestyle.width = 5
        ls.style.linestyle.color = simplekml.Color.rgb(40, 178, 250)
    stations2kml = set()
    for section, stations_edges in zip(section_list, stations_edges_list):
        for start_station_edges in stations_edges["start"]:
            stations2kml.add(
                tuple(
                    (
                        section["start"],
                        get_center_station_point(start_station_edges),
                    )
                )
            )
        for goal_station_edges in stations_edges["goal"]:
            stations2kml.add(
                tuple(
                    (
                        section["goal"],
                        get_center_station_point(goal_station_edges),
                    )
                )
            )
        if is_including_middles is True:
            for middle_station_edges in stations_edges["middle"]:
                stations2kml.add(
                    tuple(
                        (
                            middle_station_edges[0],
                            get_center_station_point(middle_station_edges[1]),
                        )
                    )
                )
        else:
            pass
    for station2kml in stations2kml:
        pnt_start = kml.newpoint(name=station2kml[0])
        pnt_start.coords = [station2kml[1]]
    if is_abs is False:
        save_abspath = relpath_to_abspath(SAVE_PATH)
    else:
        save_abspath = SAVE_PATH
    os.makedirs(os.path.dirname(save_abspath), exist_ok=True)
    kml.save(save_abspath)


def read_config(path):
    abs_path = os.path.join(os.path.dirname(__file__), path)
    with open(abs_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    section_list = config["section_list"]
    shapefile_path = config["shapefile_path"]
    is_including_middles = config["is_including_middles"]
    return (section_list, shapefile_path, is_including_middles)


def get_section_edges_list(section_list, shape_recs, patch):
    section_edges_list = list()
    station_edges_list = list()
    for section in section_list:
        (section_edges_each, station_edges_each) = get_section_edges(
            section, shape_recs, patch
        )
        section_edges_list.append(section_edges_each)
        station_edges_list.append(station_edges_each)
    return (section_edges_list, station_edges_list)


def read_patch(path):
    abs_path = os.path.join(os.path.dirname(__file__), path)
    with open(abs_path, "r", encoding="utf-8") as patch_file:
        patch = json.load(patch_file)
    for patch_each in patch:
        for i, point in enumerate(patch_each[2]):
            patch_each[2][i] = tuple(point)
    return patch


def str2bool_is(str_v):
    if str_v == "yes":
        bool_v = True
    else:
        bool_v = False
    return bool_v


def main():
    PATH_IS_ABS = False
    CONFIG_PATH = "config/config.json"
    PATCH_PATH = "patch/patch.json"
    SAVE_PATH = "kml/rail.kml"
    (section_list, shapefile_path, is_including_middles) = read_config(
        CONFIG_PATH
    )
    patch = read_patch(PATCH_PATH)
    shape_recs = read_shapefile(shapefile_path, PATH_IS_ABS)
    (section_edges_list, stations_edges_list) = get_section_edges_list(
        section_list, shape_recs, patch
    )
    is_including_middles_bool = str2bool_is(is_including_middles)
    output_kml(
        section_edges_list,
        stations_edges_list,
        section_list,
        is_including_middles_bool,
        SAVE_PATH,
        PATH_IS_ABS,
    )


if __name__ == "__main__":
    main()
