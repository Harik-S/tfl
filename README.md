# TfL Bus Journey Time Tracker

This Python script uses the TfL (Transport for London) Arrivals API to estimate the **actual travel time between two bus stops** for selected bus routes.

The program continuously monitors buses at an **origin stop** and a **destination stop**, identifies individual buses using their `vehicleId`, and records how long each bus took to travel between the two stops.

The results are exported to a CSV file for later analysis.

---

## Features

- Monitors multiple bus routes simultaneously
- Tracks individual buses using `vehicleId`
- Estimates arrival times at both stops
- Calculates journey durations between stops
- Exports results to `bus_arrivals.csv`
- Continues running even if temporary API/network errors occur

---

## How it works

Every `refresh_time` seconds:

1. The script queries the TfL Arrivals API for the origin stop.
2. It stores all currently approaching buses.
3. When a bus disappears from the arrivals list, it is assumed to have arrived at the stop.
4. The same process is repeated for the destination stop.
5. Buses are matched using their `vehicleId`.
6. If a bus is observed at both stops, its journey time is calculated.

The estimated arrival time is:

```text
current_time + timeToStation - refresh_time
```

because the bus disappeared sometime during the previous polling interval.

---

## Requirements

Python 3.9+ is recommended.

Install dependencies:

```bash
pip install requests
```

The remaining modules (`csv`, `datetime`, `time`, `os`) are part of the Python standard library.

---

## Configuration

Edit these variables near the top of the script:

```python
origin_id = "490000124HH"
end_id = "490000128A"

bus_ids = ["sl10", "183"]

refresh_time = 30
```

### Variables

| Variable | Description |
|----------|-------------|
| `origin_id` | TfL stop ID of the starting bus stop |
| `end_id` | TfL stop ID of the destination bus stop |
| `bus_ids` | List of bus routes to track |
| `refresh_time` | Time between API requests (seconds) |

---

## Finding bus stop IDs

TfL bus stop IDs can be found from:

```text
https://api.tfl.gov.uk/StopPoint/Search/<stop name>
```

or from the TfL website.

Example:

```text
490000124HH
```

---

## Output CSV format

The script creates (or appends to) `bus_arrivals.csv`.

Columns:

| Column | Description |
|--------|-------------|
| `lineId` | Bus route |
| `vehicleId` | Unique identifier of the bus |
| `origin_arrival` | Estimated arrival time at origin |
| `destination_arrival` | Estimated arrival time at destination |
| `duration_seconds` | Estimated journey time |

Example:

```csv
lineId,vehicleId,origin_arrival,destination_arrival,duration_seconds
sl10,LJ23ABC,2026-06-22T16:03:10,2026-06-22T16:11:42,512
183,LJ21XYZ,2026-06-22T16:15:28,2026-06-22T16:28:02,754
```

---

## Running the program

Execute:

```bash
python main.py
```

The program will run for 50 minutes by default.

To stop early:

```text
Ctrl + C
```

---

## Limitations

This script estimates arrival times and is not perfectly accurate.

Potential sources of error include:

- The TfL API updates periodically rather than continuously.
- Arrival times are only checked every `refresh_time` seconds.
- A bus may disappear from the arrivals list slightly before or after reaching the stop.
- If a bus terminates early, is diverted, or is withdrawn from service, no journey duration will be recorded.
- Journey durations become less accurate as `refresh_time` increases.

Reducing `refresh_time` improves accuracy but increases the number of API requests.

---

## Example use cases

- Measure real-world bus travel times
- Analyse route reliability
- Compare different bus routes
- Collect data for visualisations and statistics
- Study traffic patterns throughout the day

---

## TfL API reference

The script uses the TfL Arrivals endpoint:

```text
https://api.tfl.gov.uk/StopPoint/{stopId}/Arrivals
```

Official documentation:

https://api-portal.tfl.gov.uk/

---

## Future improvements

Possible additions:

- Plot journey times over time
- Calculate average, median and percentile journey durations
- Detect and remove outliers
- Track more than two stops
- Store data in a database instead of CSV
- Create a live dashboard
- Add visualisations using Matplotlib or Plotly
