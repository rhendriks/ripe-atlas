#!/usr/bin/env python3
"""
Simple RIPE Atlas Ping Script

Performs a simple ping measurement and saves results as .csv.gz

Usage:
    python simple_ping.py --probes <probe_ids|probe-ids.txt> --targets <target_ips|hitlist.txt> [options]
    python simple_ping.py --probes ALL --targets 8.8.8.8 --output results.csv.gz

Arguments:
    --probes: Comma-separated list of probe IDs (or path to a probe-id file), or 'ALL' for all available probes
    --targets: Comma-separated list of target IP addresses or hostnames (or path to a hitlist file)
    --output: Output file name (default: ping_results_<timestamp>.csv.gz)
    --packets: Number of ping packets to send (default: 3)
    --wait: Time to wait for measurement completion in seconds (default: 300)

TODOs:
* Support hitlist and probe-id files
* print credit costs before (wait for y/n from user)
* exit wait early when the requested measurements have all finished
* write output to output/ directory
* support IPv6

example:
ping 8.8.8.8 from all probes
python simple_ping.py --probes ALL --target 8.8.8.8
"""

import argparse
import csv
import gzip
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()

try:
    from ripe.atlas.cousteau import (
        Ping,
        AtlasSource,
        AtlasCreateRequest,
        AtlasResultsRequest,
        ProbeRequest
    )
except ImportError:
    print("Error: ripe.atlas.cousteau is not installed.")
    print("Install it with: pip install ripe.atlas.cousteau")
    sys.exit(1)

# API limit defined by RIPE Atlas
MAX_PROBES_PER_MEASUREMENT = 1000

def load_api_key() -> str:
    """Load RIPE Atlas API key from environment variable."""
    api_key = os.getenv('RIPE_ATLAS_API_KEY')
    if not api_key:
        print("Error: RIPE_ATLAS_API_KEY environment variable not set.")
        print("Please set it with your RIPE Atlas API key.")
        print("Get your key from: https://atlas.ripe.net/keys/")
        sys.exit(1)
    return api_key


def get_all_probe_ids() -> List[int]:
    """Retrieve all available probe IDs from RIPE Atlas."""
    print("Fetching all available probes...")
    probe_ids = []
    
    # Get probes with status=1 (connected)
    filters = {"status": 1}
    probes = ProbeRequest(**filters)
    
    for probe in probes:
        probe_ids.append(probe["id"])
    
    print(f"Found {len(probe_ids):,} connected probes")
    return probe_ids


def parse_probe_list(probe_arg: str) -> List[int]:
    """
    Parse probe argument.
    
    Args:
        probe_arg: Either 'ALL' or comma-separated list of probe IDs
    
    Returns:
        List of probe IDs
    """
    if probe_arg.upper() == 'ALL':
        return get_all_probe_ids()
    else:
        try:
            return [int(p.strip()) for p in probe_arg.split(',')]
        except ValueError:
            print(f"Error: Invalid probe ID format: {probe_arg}")
            sys.exit(1)


def parse_target_list(target_arg: str) -> List[str]:
    """
    Parse target argument.
    
    Args:
        target_arg: Comma-separated list of target IPs or hostnames
    
    Returns:
        List of targets
    """
    return [t.strip() for t in target_arg.split(',')]

def chunk_list(lst, n):
    """Split a list into chunks of size n."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def create_ping_measurement(
    api_key: str,
    probes: List[int],
    target: str,
    packets: int = 3,
    chunk_index: int = 1,
) -> int:
    """
    Create a ping measurement for a chunk of probes.
    
    Args:
        api_key: RIPE Atlas API key
        probes: List of probe IDs
        target: Target IP or hostname
        packets: Number of ping packets
        chunk_index: Chunk index
    
    Returns:
        Measurement ID
    """
    print(f"Creating ping measurement to {target} with {len(probes):,} probes... (Chunk {chunk_index})")
    
    # Define ping measurement
    ping = Ping(
        af=4,  # IPv4
        target=target,
        description=f"Simple ping to {target} (Chunk {chunk_index})",
        packets=packets
    )
    
    # Use specific probe IDs
    source = AtlasSource(
        type="probes",
        value=",".join(map(str, probes)),
        requested=len(probes)
    )
    
    # Create one-off measurement
    atlas_request = AtlasCreateRequest(
        key=api_key,
        measurements=[ping],
        sources=[source],
        is_oneoff=True
    )
    
    is_success, response = atlas_request.create()
    
    if is_success:
        measurement_id = response['measurements'][0]
        print(f"Measurement created with ID: {measurement_id}")
        return measurement_id
    else:
        print(f"Error creating measurement: {response}")
        sys.exit(1)


def wait_for_measurement(measurement_id: int, wait_time: int = 300):
    """Wait for measurement to complete."""
    print(f"Waiting for measurement {measurement_id} to complete...")
    print(f"This may take up to {wait_time} seconds...")
    time.sleep(wait_time)
    print("Wait complete. Fetching results...")


def fetch_measurement_results(measurement_id: int) -> List[Dict[str, Any]]:
    """
    Fetch results from a measurement.
    
    Args:
        measurement_id: Measurement ID
    
    Returns:
        List of result dictionaries
    """
    print(f"Fetching results for measurement {measurement_id}...")
    
    kwargs = {
        "msm_id": measurement_id
    }
    
    is_success, results = AtlasResultsRequest(**kwargs).create()
    
    if is_success:
        print(f"Retrieved {len(results):,} results")
        return results
    else:
        print(f"Error fetching results: {results}")
        return []


def parse_ping_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse ping results and extract relevant data.
    
    Args:
        results: List of raw measurement results
    
    Returns:
        List of parsed results with probe_id, rtt, and hop_count
    """
    parsed_results = []
    
    for result in results:
        probe_id = result.get('prb_id')
        
        # Check if result contains ping data
        if 'result' not in result:
            continue
        
        ping_results = result.get('result', [])
        
        for ping in ping_results:
            # Skip if no RTT (ping failed)
            if 'rtt' not in ping:
                continue
            
            rtt = ping.get('rtt')
            
            # Calculate hop_count from TTL
            # hop_count = initial_ttl - ttl
            # Common initial TTLs are 64, 128, 255
            ttl = ping.get('ttl')
            hop_count = None
            
            if ttl is not None:
                # Determine likely initial TTL
                if ttl <= 64:
                    initial_ttl = 64
                elif ttl <= 128:
                    initial_ttl = 128
                else:
                    initial_ttl = 255
                
                hop_count = initial_ttl - ttl
            
            parsed_results.append({
                'probe_id': probe_id,
                'rtt': rtt,
                'hop_count': hop_count if hop_count is not None else 0
            })
    
    return parsed_results


def write_results_to_csv(results: List[Dict[str, Any]], output_file: str):
    """
    Write results to compressed CSV file.
    
    Args:
        results: List of parsed results
        output_file: Output file path
    """
    print(f"Writing {len(results):,} results to {output_file}...")
    
    with gzip.open(output_file, 'wt', newline='') as csvfile:
        fieldnames = ['probe_id', 'rtt', 'hop_count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    print(f"Results written to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Simple RIPE Atlas Ping Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--probes',
        required=True,
        help='Comma-separated list of probe IDs or "ALL" for all probes'
    )
    
    parser.add_argument(
        '--targets',
        required=True,
        help='Comma-separated list of target IPs or hostnames'
    )
    
    parser.add_argument(
        '--output',
        help='Output CSV.GZ file (default: ping_results_<timestamp>.csv.gz)'
    )
    
    parser.add_argument(
        '--packets',
        type=int,
        default=3,
        help='Number of ping packets to send (default: 3)'
    )
    
    parser.add_argument(
        '--wait',
        type=int,
        default=300,
        help='Time to wait for measurement completion in seconds (default: 300)'
    )
    
    args = parser.parse_args()
    
    # Load API key
    api_key = load_api_key()
    
    # Parse probes and targets
    probes = parse_probe_list(args.probes)
    targets = parse_target_list(args.targets)
    
    print(f"Using {len(probes):,} probes")
    print(f"Targeting {len(targets):,} destination(s): {', '.join(targets)}")
    
    # Set default output file if not provided
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f"ping_results_{timestamp}.csv.gz"
    
    # Collect all results
    all_results = []
    
    # Create measurements for each target
    measurement_ids = []

    for target in targets:
        print(f"Targeting: {target}")
        # Split probes into chunks of 1k
        for idx, probe_chunk in enumerate(chunk_list(probes, MAX_PROBES_PER_MEASUREMENT), 1):
            msm_id = create_ping_measurement(api_key, probe_chunk, target, args.packets, idx)
            measurement_ids.append(msm_id)
            # Short sleep to avoid hitting API rate limits or overwhelming target
            time.sleep(1)
    
    # Wait for measurements to complete
    wait_for_measurement(measurement_ids[0], args.wait)
    
    # Fetch and parse results
    for measurement_id in measurement_ids:
        results = fetch_measurement_results(measurement_id)
        parsed = parse_ping_results(results)
        all_results.extend(parsed)
    
    # Write results to CSV
    if all_results:
        write_results_to_csv(all_results, args.output)
        print(f"\nSuccess! Total results: {len(all_results):,}")
    else:
        print("Warning: No results were collected")
        sys.exit(1)


if __name__ == '__main__':
    main()
