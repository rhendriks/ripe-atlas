# RIPE Atlas Scripts

A collection of scripts for working with [RIPE Atlas](https://atlas.ripe.net/), a global network measurement platform.

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/rhendriks/ripe-atlas.git
   cd ripe-atlas
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the example environment file and add your API key:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your RIPE Atlas API key:
   - Get your API key from: https://atlas.ripe.net/keys/
   - Replace `your_api_key_here` with your actual API key

5. (Optional) Install the RIPE Atlas Python library:
   ```bash
   pip install ripe.atlas.cousteau
   ```

## Repository Structure

```
.
├── probe_selection/     # Scripts to select and filter RIPE Atlas probes
├── measurements/        # Scripts to create and run measurements
├── analysis/            # Scripts to analyse measurement results
├── .env.example         # Example environment configuration
└── .env                 # Your local environment configuration (not tracked in git)
```

## Directories

### `probe_selection/`
Contains scripts for selecting RIPE Atlas probes based on various criteria such as:
- Geographic location
- AS number
- Probe status and capabilities
- Custom filters
- **`get_probe_data.py`**: Enrich CSV.GZ files with probe metadata (country, city, coordinates, IP addresses, ASN)

See [probe_selection/README.md](probe_selection/README.md) for more details.

### `measurements/`
Contains scripts for creating and managing RIPE Atlas measurements:
- Ping measurements
- Traceroute measurements
- DNS queries
- HTTP/HTTPS requests
- SSL/TLS certificate checks

See [measurements/README.md](measurements/README.md) for more details.

## Resources

- [RIPE Atlas Website](https://atlas.ripe.net/)
- [RIPE Atlas API Documentation](https://atlas.ripe.net/docs/apis/)
- [Cousteau Library Documentation](https://ripe-atlas-cousteau.readthedocs.io/)
- [RIPE Atlas Community](https://atlas.ripe.net/community/)

## License

See [LICENSE](LICENSE) file for details.
