#
# Copyright 2015 Smerle Inc. All rights reserved
#

__author__ = 'thomasr'
from pprint import pprint
# from HereAPI import geocode


def routing(client, origin, destination, mode=None, departure_time=None, arrival_time=None):
    params={}
    pprint(departure_time)
    oS = "geo!" + str(origin["Lat"]) + "," + str(origin["Lon"])
    dS = "geo!" + str(destination["Lat"]) + "," + str(destination["Lon"])
    if origin:
        params["waypoint0"] = oS
        params["waypoint1"] = dS
        params["metricSystem"] = "imperial"
        params["mode"] = mode
        params["instructionFormatType"] = "txt"
        params["departure"] = departure_time
        # params["routeattributes"] = "sh,bb,gr"
        # params["departure"] = "now"
        # params["avoidTransportTypes"] = "busPublic,busTouristic,busIntercity,busExpress"
        # params["alternatives"] = 3
        # params["maxnumberofchanges"] = 1
    response = client._get("https://route.api.here.com/routing/7.2/calculateroute.json", params)
    # response = client._get("https://route.cit.api.here.com/routing/7.2/calculateroute.json", params)
    # response = {}
    return response
