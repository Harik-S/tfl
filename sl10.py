import csv
import requests
from datetime import datetime, timedelta
import time
import os

origin_id = "490000124HH"
end_id = "490000128A"

bus_ids = ["sl10", "183"]

refresh_time = 30


def get_response(stop_id):
    url = f"https://api.tfl.gov.uk/StopPoint/{stop_id}/Arrivals"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        # on any network or parsing error return empty list so code can continue
        return []



times_origin = {bus: [] for bus in bus_ids}
times_destination = {bus: [] for bus in bus_ids}

# maps lineId -> {vehicleId: timeToStation_seconds}
arrival_times_origin = {bus: {} for bus in bus_ids}
arrival_times_destination = {bus: {} for bus in bus_ids}

end_program_time = datetime.now() + timedelta(hours=6)

try:
    while True:
        if datetime.now() >= end_program_time:
            break

        response = get_response(origin_id)

        for bus_id in bus_ids:
            buses = [b for b in response if b.get("lineId") == bus_id]

            old_plates = set(arrival_times_origin[bus_id].keys())
            new_plates = set(b.get("vehicleId") for b in buses if b.get("vehicleId") is not None)
            removed_plates = old_plates - new_plates
            for vid in removed_plates:
                secs = arrival_times_origin[bus_id].get(vid)
                if secs is None:
                    continue
                # approximate arrival time when it disappeared from the stop's arrivals
                time_arrival = datetime.now() + timedelta(seconds=secs) - timedelta(seconds=refresh_time)
                times_origin[bus_id].append([vid, time_arrival])

        
        # update current origin arrivals
        for bus_id in bus_ids:
            response = get_response(origin_id)
            buses = [b for b in response if b.get("lineId") == bus_id]
            arrival_times_origin[bus_id] = {b.get("vehicleId"): int(b.get("timeToStation", 0)) for b in buses if b.get("vehicleId")}

        response = get_response(end_id)

        for bus_id in bus_ids:
            buses = [b for b in response if b.get("lineId") == bus_id]

            old_plates = set(arrival_times_destination[bus_id].keys())
            new_plates = set(b.get("vehicleId") for b in buses if b.get("vehicleId") is not None)
            removed_plates = old_plates - new_plates
            for vid in removed_plates:
                secs = arrival_times_destination[bus_id].get(vid)
                if secs is None:
                    continue
                time_end = datetime.now() + timedelta(seconds=secs) - timedelta(seconds=refresh_time)
                times_destination[bus_id].append([vid, time_end])

        # update current destination arrivals
        for bus_id in bus_ids:
            response = get_response(end_id)
            buses = [b for b in response if b.get("lineId") == bus_id]
            arrival_times_destination[bus_id] = {b.get("vehicleId"): int(b.get("timeToStation", 0)) for b in buses if b.get("vehicleId")}

        print("\nOrigin:")
        print(times_origin)

        print("\nDestination:")
        print(times_destination)

        time.sleep(refresh_time)
except KeyboardInterrupt:
    # allow graceful stop
    pass

durations = {bus: [] for bus in bus_ids}

csv_file = "bus_arrivals.csv"
write_header = not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0
with open(csv_file, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    if write_header:
        writer.writerow(["lineId", "vehicleId", "origin_arrival", "destination_arrival", "duration_seconds"])

    for i in bus_ids:
        for j in times_origin[i]:
            found = False
            for k in times_destination[i]:
                if j[0] == k[0] and not found:
                    print(f"Bus {i} with vehicle ID {j[0]} arrived at origin at {j[1]} and at destination at {k[1]}.")
                    duration_seconds = (k[1] - j[1]).total_seconds()
                    durations[i].append([k[1], duration_seconds])
                    writer.writerow([i, j[0], j[1].isoformat(), k[1].isoformat(), duration_seconds])
                    found = True

            if not found:
                print(f"Bus {i} with vehicle ID {j[0]} arrived at origin at {j[1]} but did not arrive at destination.")
                writer.writerow([i, j[0], j[1].isoformat(), "", ""])


        