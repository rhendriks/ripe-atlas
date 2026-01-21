#!/usr/bin/env python3
"""
Test script for simple_ping.py

This script tests the parsing logic without making actual API calls.
"""

import sys
import os
import gzip
import csv
from simple_ping import parse_ping_results, write_results_to_csv


def test_parse_ping_results():
    """Test the parse_ping_results function with sample data."""
    
    # Sample ping results (simulating RIPE Atlas API response)
    sample_results = [
        {
            'prb_id': 1001,
            'result': [
                {'rtt': 10.5, 'ttl': 54},
                {'rtt': 11.2, 'ttl': 54},
                {'rtt': 10.8, 'ttl': 54}
            ]
        },
        {
            'prb_id': 1002,
            'result': [
                {'rtt': 25.3, 'ttl': 120},
                {'rtt': 26.1, 'ttl': 120}
            ]
        },
        {
            'prb_id': 1003,
            'result': [
                {'rtt': 5.5, 'ttl': 63},
                {'ttl': 63}  # Failed ping (no rtt) - should be skipped
            ]
        }
    ]
    
    # Parse results
    parsed = parse_ping_results(sample_results)
    
    # Verify results
    print("Testing parse_ping_results...")
    print(f"Parsed {len(parsed)} results")
    
    # Should have 6 results (3 + 2 + 1, skipping 1 failed ping)
    assert len(parsed) == 6, f"Expected 6 results, got {len(parsed)}"
    
    # Check first result
    assert parsed[0]['probe_id'] == 1001
    assert parsed[0]['rtt'] == 10.5
    assert parsed[0]['hop_count'] == 10  # 64 - 54
    
    # Check probe 1002 (TTL 120, initial should be 128)
    probe_1002_results = [r for r in parsed if r['probe_id'] == 1002]
    assert len(probe_1002_results) == 2
    assert probe_1002_results[0]['hop_count'] == 8  # 128 - 120
    
    print("✓ parse_ping_results tests passed")


def test_write_and_read_csv():
    """Test writing and reading CSV.GZ file."""
    
    test_results = [
        {'probe_id': 1001, 'rtt': 10.5, 'hop_count': 10},
        {'probe_id': 1002, 'rtt': 25.3, 'hop_count': 8},
        {'probe_id': 1003, 'rtt': 5.5, 'hop_count': 1}
    ]
    
    test_file = '/tmp/test_ping_results.csv.gz'
    
    # Write results
    print("Testing write_results_to_csv...")
    write_results_to_csv(test_results, test_file)
    
    # Read back and verify
    print("Reading back results...")
    with gzip.open(test_file, 'rt', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}"
    assert rows[0]['probe_id'] == '1001'
    assert float(rows[0]['rtt']) == 10.5
    assert int(rows[0]['hop_count']) == 10
    
    print("✓ CSV write/read tests passed")
    
    # Clean up
    os.remove(test_file)


def test_probe_parsing():
    """Test probe list parsing."""
    from simple_ping import parse_target_list
    
    print("Testing parse_target_list...")
    
    # Single target
    targets = parse_target_list("8.8.8.8")
    assert targets == ["8.8.8.8"], f"Expected ['8.8.8.8'], got {targets}"
    
    # Multiple targets
    targets = parse_target_list("8.8.8.8, 1.1.1.1, example.com")
    assert len(targets) == 3
    assert targets[0] == "8.8.8.8"
    assert targets[1] == "1.1.1.1"
    assert targets[2] == "example.com"
    
    print("✓ Probe parsing tests passed")


def main():
    """Run all tests."""
    print("Running simple_ping.py tests...\n")
    
    try:
        test_parse_ping_results()
        test_write_and_read_csv()
        test_probe_parsing()
        
        print("\n✓ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
