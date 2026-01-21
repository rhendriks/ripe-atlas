# Measurement Scripts

This directory contains scripts to perform RIPE Atlas measurements.

## Purpose

Use these scripts to:
- Create and run RIPE Atlas measurements (ping, traceroute, DNS, HTTP, etc.)
- Retrieve measurement results
- Analyze measurement data
- Schedule recurring measurements

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
