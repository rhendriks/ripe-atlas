#!/usr/bin/env python3
"""
Script to add probe metadata to CSV files or pandas DataFrames.

Takes a .csv.gz file with a 'probe_id' column and adds metadata for each probe:
- country
- city
- lat
- lon
- ipv4 (IPv4 address)
- ipv6 (IPv6 address)
- asn

Unknown values for a particular probe will be NaN.

Public Functions:
    enrich_dataframe_with_probe_metadata(df, verbose=True): 
        Enriches a pandas DataFrame containing a 'probe_id' column with probe metadata.
        Can be imported for use in notebooks or other scripts.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd
import requests


# Default metadata structure for probes with missing/unavailable data
DEFAULT_METADATA = {
    'country': None,
    'city': None,
    'lat': None,
    'lon': None,
    'ipv4': None,
    'ipv6': None,
    'asn': None,
}


def fetch_probe_metadata(probe_id):
    """
    Fetch metadata for a single probe from RIPE Atlas API.
    
    Args:
        probe_id: The probe ID to fetch metadata for
        
    Returns:
        dict: Probe metadata with keys: country, city, lat, lon, ipv4, ipv6, asn
    """
    url = f"https://atlas.ripe.net/api/v2/probes/{probe_id}/"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract coordinates once to avoid repeated lookups
        geometry = data.get('geometry')
        coordinates = geometry.get('coordinates', [None, None]) if geometry else [None, None]
        
        # Extract metadata from the response
        metadata = {
            'country': data.get('country_code'),
            'city': data.get('city'),
            'lat': coordinates[1],
            'lon': coordinates[0],
            'ipv4': data.get('address_v4'),
            'ipv6': data.get('address_v6'),
            'asn': data.get('asn_v4'),
        }
        
        return metadata
        
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Could not fetch metadata for probe {probe_id}: {e}", file=sys.stderr)
        return DEFAULT_METADATA.copy()


def enrich_dataframe_with_probe_metadata(df, verbose=True):
    """
    Add probe metadata columns to a pandas DataFrame containing a 'probe_id' column.
    
    This function enriches a DataFrame with probe metadata fetched from the RIPE Atlas API.
    For each unique probe_id, it fetches and adds the following columns:
    - country: Country code
    - city: City name
    - lat: Latitude
    - lon: Longitude
    - ipv4: IPv4 address
    - ipv6: IPv6 address
    - asn: Autonomous System Number
    
    Args:
        df: pandas DataFrame with a 'probe_id' column
        verbose: If True, print progress messages (default: True)
        
    Returns:
        pandas DataFrame: A copy of the input DataFrame with added metadata columns
        
    Raises:
        ValueError: If the DataFrame does not contain a 'probe_id' column
        
    Example:
        >>> import pandas as pd
        >>> from probe_selection.get_probe_data import enrich_dataframe_with_probe_metadata
        >>> df = pd.DataFrame({'probe_id': [1, 2, 3], 'value': [10, 20, 30]})
        >>> enriched_df = enrich_dataframe_with_probe_metadata(df)
        >>> print(enriched_df.columns)
    """
    # Check if 'probe_id' column exists
    if 'probe_id' not in df.columns:
        raise ValueError("DataFrame must contain a 'probe_id' column")
    
    # Create a copy to avoid modifying the original dataframe
    result_df = df.copy()
    
    if verbose:
        print(f"Found {len(result_df)} rows with probe IDs")
    
    # Get unique probe IDs to avoid duplicate API calls
    unique_probe_ids = result_df['probe_id'].unique()
    if verbose:
        print(f"Fetching metadata for {len(unique_probe_ids)} unique probes...")
    
    # Fetch metadata for each unique probe
    probe_metadata = {}
    for i, probe_id in enumerate(unique_probe_ids, 1):
        if pd.notna(probe_id):
            if verbose and i % 10 == 0:
                print(f"Progress: {i}/{len(unique_probe_ids)} probes")
            try:
                probe_metadata[probe_id] = fetch_probe_metadata(int(probe_id))
            except (ValueError, TypeError) as e:
                if verbose:
                    print(f"Warning: Invalid probe_id '{probe_id}': {e}", file=sys.stderr)
                probe_metadata[probe_id] = DEFAULT_METADATA.copy()
        else:
            probe_metadata[probe_id] = DEFAULT_METADATA.copy()
    
    if verbose:
        print("Adding metadata columns to dataframe...")
    
    # Add metadata columns to the dataframe using a single map operation
    metadata_df = result_df['probe_id'].map(lambda x: probe_metadata.get(x, DEFAULT_METADATA)).apply(pd.Series)
    for col in DEFAULT_METADATA.keys():
        result_df[col] = metadata_df[col]
    
    if verbose:
        print(f"Successfully enriched {len(result_df)} rows")
    
    return result_df


def add_probe_metadata(input_file, output_file=None):
    """
    Add probe metadata to a CSV.GZ file.
    
    Args:
        input_file: Path to input .csv.gz file with 'probe_id' column
        output_file: Path to output .csv.gz file (defaults to input_file with '_enriched' suffix)
    """
    # Determine output file path
    if output_file is None:
        input_path = Path(input_file)
        if input_path.suffix == '.gz':
            base = input_path.stem
            if base.endswith('.csv'):
                base = base[:-4]
            output_file = input_path.parent / f"{base}_enriched.csv.gz"
        else:
            output_file = input_path.parent / f"{input_path.stem}_enriched{input_path.suffix}.gz"
    
    print(f"Reading input file: {input_file}")
    
    # Read the input CSV.GZ file
    try:
        df = pd.read_csv(input_file, compression='gzip')
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Enrich the dataframe using the public function
    try:
        enriched_df = enrich_dataframe_with_probe_metadata(df, verbose=True)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write the enriched dataframe to output file
    print(f"Writing output file: {output_file}")
    enriched_df.to_csv(output_file, compression='gzip', index=False)
    
    print(f"Successfully saved enriched data to {output_file}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Add probe metadata to CSV.GZ files with probe_id column'
    )
    parser.add_argument(
        'input_file',
        help='Path to input .csv.gz file with probe_id column'
    )
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Path to output .csv.gz file (default: input_file with _enriched suffix)'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    add_probe_metadata(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
