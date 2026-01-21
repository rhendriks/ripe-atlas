# Measurement Scripts

This directory contains scripts to perform RIPE Atlas measurements.

## Purpose

Use these scripts to:
- Create and run RIPE Atlas measurements (ping, traceroute, DNS, HTTP, etc.)
- Retrieve measurement results
- Analyze measurement data
- Schedule recurring measurements

## Available Scripts

### `simple_ping.py`

A simple script to perform ping measurements and export results to compressed CSV.

**Features:**
- Ping from specific probes or all available probes
- Support for single or multiple targets
- Export results to `.csv.gz` format
- Extracts probe_id, RTT, and hop_count (derived from TTL)

**Usage:**
```bash
# Ping a single target from specific probes
python simple_ping.py --probes 1001,1002,1003 --targets 8.8.8.8

# Ping multiple targets from all probes
python simple_ping.py --probes ALL --targets 8.8.8.8,1.1.1.1

# Specify output file and wait time
python simple_ping.py --probes 1001,1002 --targets example.com --output results.csv.gz --wait 120
```

**Arguments:**
- `--probes`: Comma-separated list of probe IDs or 'ALL' for all available probes
- `--targets`: Comma-separated list of target IPs or hostnames
- `--output`: Output file name (default: `ping_results_<timestamp>.csv.gz`)
- `--packets`: Number of ping packets to send (default: 3)
- `--wait`: Time to wait for measurement completion in seconds (default: 300)

**Output Format:**
The script generates a compressed CSV file with the following columns:
- `probe_id`: uint32 - RIPE Atlas probe ID
- `rtt`: float32 - Round-trip time in milliseconds
- `hop_count`: uint8 - Number of hops (derived from TTL)

## Usage

Place your measurement scripts in this directory. Common measurement types:
- **Ping**: Test reachability and latency
- **Traceroute**: Discover network paths
- **DNS**: Query DNS records
- **HTTP**: Test web service availability
- **SSL/TLS**: Check certificate validity

## Example Script Structure

```python
# example_measurement.py
import os
from datetime import datetime
from ripe.atlas.cousteau import (
    Ping,
    AtlasSource,
    AtlasCreateRequest
)

# Load API key from environment
api_key = os.getenv('RIPE_ATLAS_API_KEY')

# Define measurement
ping = Ping(
    af=4,
    target="example.com",
    description="Example ping measurement"
)

# Select probes (you can use probe IDs from probe_selection scripts)
source = AtlasSource(
    type="area",
    value="WW",
    requested=5
)

# Create measurement
atlas_request = AtlasCreateRequest(
    key=api_key,
    measurements=[ping],
    sources=[source],
    is_oneoff=True
)

# Execute
(is_success, response) = atlas_request.create()

if is_success:
    print(f"Measurement created with ID: {response['measurements'][0]}")
else:
    print(f"Error: {response}")
```

## Resources

- [RIPE Atlas Measurement API Documentation](https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/)
- [Cousteau Library](https://ripe-atlas-cousteau.readthedocs.io/)
- [Measurement Types](https://atlas.ripe.net/docs/built-in-measurements/)
