# Probe Selection Scripts

This directory contains scripts to create lists of RIPE Atlas probe IDs and enrich data with probe metadata.

## Purpose

Use these scripts to:
- Select probes based on specific criteria (location, tags, status, etc.)
- Generate probe ID lists for measurements
- Filter probes by availability, connectivity type, or other attributes
- Add probe metadata to CSV files with probe IDs

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

## Scripts

### get_probe_data.py

Adds probe metadata to CSV.GZ files containing a `probe_id` column.

**Usage:**
```bash
python3 get_probe_data.py input_file.csv.gz
```

**Options:**
- `-o, --output`: Specify output file path (default: `input_file_enriched.csv.gz`)

**Added columns:**
- `country`: Country code (e.g., "NL", "US")
- `city`: City name
- `lat`: Latitude
- `lon`: Longitude
- `ipv4`: IPv4 address
- `ipv6`: IPv6 address
- `asn`: Autonomous System Number

Unknown values will be `NaN`.

**Example:**
```bash
# Add probe metadata to a CSV file
python3 probe_selection/get_probe_data.py measurements.csv.gz

# Specify custom output file
python3 probe_selection/get_probe_data.py measurements.csv.gz -o enriched_measurements.csv.gz
```

## Resources

- [RIPE Atlas Probe API Documentation](https://atlas.ripe.net/docs/apis/rest-api-manual/probes/)
- [Cousteau Library](https://ripe-atlas-cousteau.readthedocs.io/)
