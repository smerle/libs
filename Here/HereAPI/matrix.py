__author__ = 'thomasr'
from pprint import pprint


def matrix(client, origin, destination_list, mode=None, departure_time=None):
    params = {}
    # pprint(departure_time)
    if origin:
        os = "geo!" + str(origin["Lat"]) + "," + str(origin["Lon"])
        params["start0"] = os
        params["metricSystem"] = "imperial"
        params["mode"] = mode
        # params["instructionFormatType"] = "txt"
        params["departure"] = departure_time
        # params["routeattributes"] = "sh,bb,gr"
        # params["departure"] = "now"
        # params["avoidTransportTypes"] = "busPublic,busTouristic,busIntercity,busExpress"
        # params["alternatives"] = 3
        # params["maxnumberofchanges"] = 1
        for index in range(len(destination_list)):
            dest_str = "destination" + str(index)
            ds = "geo!" + str(destination_list[index]["Lat"]) + "," + str(destination_list[index]["Lon"])
            params[dest_str] = ds
    response = client._get("https://legacy.matrix.route.cit.api.here.com/routing/6.2/calculatematrix.json", params)
    # response = client._get("https://legacy.matrix.route.api.here.com/routing/6.2/calculatematrix.json", params)
    return response
