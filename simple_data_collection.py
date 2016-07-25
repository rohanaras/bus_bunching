import datetime


def get_json(suffix):
    import urllib, json
    key = 'f0d2025d-3221-4cb0-860c-4466ccc1b0b0'
    url_object = urllib.urlopen('http://api.pugetsound.onebusaway.org/api/where/' + suffix + '.json?key=' + key)
    return json.loads(url_object.read())


def get_trip_data(trip_str, route_num):
    """
    important stuff is here:
    http://developer.onebusaway.org/modules/onebusaway-application-modules/1.1.13/api/where/elements/trip-status.html
    """
    select_data = {'trip_id': trip_str}
    suffix = 'trip-details/' + trip_str
    raw_data = get_json(suffix)
    select_data['timestamp'] = datetime.datetime.now()

    route_info = next(x for x in raw_data['data']['references']['trips'] if x['id'] == trip_str)
    select_data['route_num'] = route_num
    select_data['route_id'] = route_info['routeId']
    select_data['trip_head_sign'] = route_info['tripHeadsign']

    trip_schedule = raw_data['data']['entry']['schedule']
    select_data['previous_trip'] = trip_schedule['previousTripId']
    select_data['next_trip'] = trip_schedule['nextTripId']

    trip_status = raw_data['data']['entry']['status']
    try:
        select_data['lat'] = trip_status['position']['lat']
        select_data['lon'] = trip_status['position']['lon']
    except TypeError:
        select_data['lat'] = None
        select_data['lon'] = None
    select_data['delay'] = trip_status['scheduleDeviation']  # seconds
    select_data['closest_stop'], select_data['next_stop'] = trip_status['closestStop'], trip_status['nextStop']
    select_data['realtime'] = trip_status['predicted']
    select_data['distance_traveled'] = trip_status['distanceAlongTrip']
    select_data['total_trip_distance'] = trip_status['totalDistanceAlongTrip']

    try:
        next_stop_idx = next(index for (index, x) in enumerate(raw_data['data']['entry']['schedule']['stopTimes'])
                                        if x['stopId'] == trip_status['nextStop']) - 1
    except StopIteration:
        next_stop_idx = len(raw_data['data']['entry']['schedule']['stopTimes']) - 1
    if next_stop_idx > 0:
        select_data['last_stop'] = raw_data['data']['entry']['schedule']['stopTimes'][next_stop_idx]['stopId']

    return select_data


def get_route_trips(route_id):
    suffix = 'trips-for-route/' + route_id
    raw_data = get_json(suffix)
    return [x['id'] for x in raw_data['data']['references']['trips'] if x['routeId'] == route_id]


def get_agency_routes(agency_id):
    suffix = 'routes-for-agency/' + agency_id
    raw_data = get_json(suffix)
    return raw_data['data']['list']


if __name__ == "__main__":
    import argparse
    import pandas as pd
    import pause

    parser = argparse.ArgumentParser("Get data for a specified route for a specified amount of time")
    parser.add_argument("routes", help="Route", nargs='+', type=str)  # change this to accept list of routes -!-
    parser.add_argument("num_hours", help="Number of hours to run for", type=int)

    args = parser.parse_args()

    kcm_routes = get_agency_routes('1')
    route_ids = {x['shortName']: x['id'] for x in kcm_routes if x['shortName'] in args.routes}
    print route_ids

    date = datetime.datetime.now()
    date_string = date.strftime("%Y%m%d-%H%M")
    wait_time = 1
    next_checkpoint = wait_time
    with open('data/oba_dat-r%s-%s.csv' % ('_'.join(args.routes), date_string), 'w') as f:
        header = True
        while datetime.datetime.now() - date < datetime.timedelta(hours=args.num_hours):
            df = pd.DataFrame([get_trip_data(trip_id, route_num) for route_num in route_ids
                               for trip_id in get_route_trips(route_ids[route_num])])
            df.to_csv(f, header=header)
            header = False
            print df
            pause.until(date + datetime.timedelta(minutes=next_checkpoint))
            next_checkpoint += wait_time

