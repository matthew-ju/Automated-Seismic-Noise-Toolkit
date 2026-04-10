# Automated Seismic Noise Toolkit

[![Python](https://img.shields.io/badge/python-3.9+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Grafana](https://img.shields.io/badge/integration-Grafana-orange.svg)](https://grafana.com/)

An automated continuous data pipeline for computing, tracking, and visualizing Power Spectral Density (PSD) from seismic signals. Modified from the [IRIS DMC Noise Toolkit](https://github.com/iris-edu/noise-toolkit) for the Berkeley Seismology Lab.

## Architecture & Features

- **Automated Data Processing Pipeline:** Fetch, compute, and parse PSD data across continuous seismic waveforms at scale.
- **Signal Frequency Extraction:** Implements `ntk_autoPSD.py` to filter computed PSD files, extracting target threshold values and tracking frequency shifts across designated timespans.
- **Real-Time Telemetry:** Streams output metrics directly to a Graphite backend via `netcat` wrappers, enabling real-time seismic observability on Grafana dashboards.
- **Secure Configuration:** Employs `.env` for credential management alongside modular JSON configurations (`param/autoPSD.json`) for pipeline parameters.

## Installation

Requires Python 3.9+.

```bash
pip install -r requirements.txt
```

.env file is used for telemetry; if you don't require a Graphite server running, the data will be saved as text files in the data/ directory.
Create a `.env` file in the project root:
```env
ADM_EMAILS=admin@example.com
GRAPHITE_URL=your.graphite.host
GRAPHITE_PORT=2003
```

## Usage

Define target telemetry parameters in `param/autoPSD.json` and execute the pipeline:

```bash
python bin/ntk_autoPSD.py
```

Extracted data is logged to `data/psdPr/` and automatically forwarded to the configured Graphite server.

**Sample Log Output:**
```text
2023-01-29  01:00:00    -57
2023-01-29  01:30:00    -57
2023-01-29  02:00:00    -57
2023-01-29  02:30:00    -56
```

## Acknowledgments
- Toolkit foundation derived from the [IRIS DMC Noise Toolkit](https://github.com/iris-edu/noise-toolkit).
- Original Berkeley Seismology Lab implementation by Sylvester Seo.
- System modernization, secure configuration, and automated telemetry integration contributed by Matthew Ju (@matthewju).
