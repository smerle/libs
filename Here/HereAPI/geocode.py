#
# Copyright 2015 Smerle Inc. All rights reserved
#

__author__ = 'thomasr'
from pprint import pprint


def geocode(client, address=None):
    """
    Geocoding is the process of converting addresses
    (like ``"1600 Amphitheatre Parkway, Mountain View, CA"``) into geographic
    coordinates (like latitude 37.423021 and longitude -122.083739), which you
    can use to place markers or position the map.

    :param address: The address to geocode.
    :type address: string

    :rtype: list of geocoding results.

    """
    params = {}
    if address:
        params["searchtext"] = address
        params["gen"] = 8
        # pprint(address)
    NavLocation = {}
    resp = client._get("https://geocoder.cit.api.here.com/6.2/geocode.json", params)
    # pprint(resp)
    assert len(resp["Response"]["View"]) == 1, "No views found in response"
    # pprint("++++++++++++++++++++++++++++++++++++++++")
    for result_count in range(0, len(resp["Response"]["View"][0]["Result"])):
        MatchType = resp["Response"]["View"][0]["Result"][result_count]["MatchType"]
        if MatchType == "pointAddress":
            # pprint("PointAddress")
            NavLocation["Lat"] = \
                resp["Response"]["View"][0]["Result"][result_count]["Location"]["NavigationPosition"][0]["Latitude"]
            NavLocation["Lon"] = \
                resp["Response"]["View"][0]["Result"][result_count]["Location"]["NavigationPosition"][0]["Longitude"]
        else:
            if MatchType == "interpolated":
                # pprint("interpolated")
                NavLocation["Lat"] = \
                resp["Response"]["View"][0]["Result"][result_count]["Location"]["NavigationPosition"][0]["Latitude"]
                NavLocation["Lon"] = \
                resp["Response"]["View"][0]["Result"][result_count]["Location"]["NavigationPosition"][0]["Longitude"]

    # pprint("========================================")
    # pprint(gcode["Response"]["View"][0]["Result"][0]["Location"]["NavigationPosition"])
    # pprint("========================================")
    # pprint(gcode["Response"]["View"][0]["Result"][1]["Location"]["NavigationPosition"])
    # pprint("========================================")
    # pprint(NavLocation)
    return NavLocation

