#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

import shapefile


def relpath_to_abspath(rel_path):
    abs_path = os.path.join(os.path.dirname(__file__), rel_path)
    return abs_path


def read_station_shapefile(path, is_abs):
    if is_abs is False:
        abspath = relpath_to_abspath(path["station"])
    else:
        abspath = path["station"]
    shape_recs_station = shapefile.Reader(
        abspath, encoding="shift_jis"
    ).shapeRecords()
    return shape_recs_station


def read_config(path):
    abs_path = os.path.join(os.path.dirname(__file__), path)
    with open(abs_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    shapefile_path = config["shapefile_path"]
    return shapefile_path


def make_stations_dict(shape_recs_station):
    stations = set()
    for shape_rec_station in shape_recs_station:
        stations.add(
            tuple(
                [
                    shape_rec_station.record[3],
                    shape_rec_station.record[2],
                    shape_rec_station.record[4],
                ]
            )
        )
    stations_dict = dict()
    for station in stations:
        if station[0] not in stations_dict.keys():
            stations_dict.update({station[0]: dict()})
        else:
            pass
        if station[1] not in stations_dict[station[0]].keys():
            stations_dict[station[0]].update({station[1]: list()})
        else:
            pass
        stations_dict[station[0]][station[1]].append(station[2])
    return stations_dict


def output_stations_dict(stations_dict, SAVE_PATH):
    save_abspath = relpath_to_abspath(SAVE_PATH)
    os.makedirs(os.path.dirname(save_abspath), exist_ok=True)
    with open(save_abspath, "w", encoding="utf-8") as stations_dict_file:
        json.dump(
            stations_dict, stations_dict_file, indent=4, ensure_ascii=False
        )


def main():
    CONFIG_PATH = "config/config.json"
    SAVE_PATH = "dict/stations_dict.json"
    PATH_IS_ABS = False
    shapefile_path = read_config(CONFIG_PATH)
    shape_recs_station = read_station_shapefile(shapefile_path, PATH_IS_ABS)
    stations_dict = make_stations_dict(shape_recs_station)
    output_stations_dict(stations_dict, SAVE_PATH)


if __name__ == "__main__":
    main()
