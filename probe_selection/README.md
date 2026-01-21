# Probe Selection Scripts

This directory contains scripts to create lists of RIPE Atlas probe IDs.

## Purpose

Use these scripts to:
- Select probes based on specific criteria (location, tags, status, etc.)
- Generate probe ID lists for measurements
- Filter probes by availability, connectivity type, or other attributes

## Usage

Place your probe selection scripts in this directory. Common examples:
- Selecting probes by country code
- Filtering probes by ASN
- Finding probes with specific capabilities
- Creating custom probe sets for measurements

## Example Script Structure

```python
# example_probe_selection.py
import os
from ripe.atlas.cousteau import ProbeRequest

# Load API key from environment
api_key = os.getenv('RIPE_ATLAS_API_KEY')

# Example: Get probes from a specific country
filters = {"country_code": "NL", "status": 1}
probes = ProbeRequest(**filters)

probe_list = []
for probe in probes:
    probe_list.append(probe["id"])

print(f"Found {len(probe_list)} probes")
print(probe_list)
```

## Resources

- [RIPE Atlas Probe API Documentation](https://atlas.ripe.net/docs/apis/rest-api-manual/probes/)
- [Cousteau Library](https://ripe-atlas-cousteau.readthedocs.io/)
