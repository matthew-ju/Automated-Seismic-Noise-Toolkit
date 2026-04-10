# Automated Seismic Noise Toolkit (Berkeley Seismology Lab)

[![Python](https://img.shields.io/badge/python-3.9+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Grafana](https://img.shields.io/badge/integration-Grafana-orange.svg)](https://grafana.com/)

An automated continuous data pipeline for computing, tracking, and visualizing Power Spectral Density (PSD) from seismic signals. 

This repository is a heavily modified version of the [IRIS DMC Noise Toolkit](https://github.com/iris-edu/noise-toolkit), customized specifically for the **Berkeley Seismology Lab**. It provides extended functionalities for tracking specific seismic frequency periods, and shipping those metrics over a network to a Graphite server for real-time visualization on **Grafana**. 

## ✨ Key Enhancements & Features

* **Automated Data Processing**: Scripts to fetch data, compute the PSD of continuous seismic waveforms, and parse enormous output datasets entirely hands-off.
* **Period Extraction**: Features `ntk_autoPSD.py`, a robust Python pipeline that filters calculated PSD files to track specific period thresholds and isolate frequency shifts over large timespans.
* **Real-time Telemetry via Graphite**: Built-in support to stream seismic metrics directly into a `netcat` Graphite cache via Python's `subprocess`, making seismic noise metrics observable on Grafana dashboard.
* **Modernized Configurations**: Secure parameter handling and environment variables utilizing `dotenv` and JSON configurations (`param/autoPSD.json`).

## 🛠 Prerequisites

Make sure you have Python 3.9+ installed. You can install all necessary packages by running:

```bash
pip install -r requirements.txt
```

Set up your environment variables by creating a `.env` file at the project root with the following structure:
```env
ADM_EMAILS=admin@example.com
GRAPHITE_URL=your.graphite.host
GRAPHITE_PORT=2003
```

## 🚀 Usage

### `ntk_autoPSD.py`

Given a time period, station, and desired frequency in `param/autoPSD.json`, this script drives the entire pipeline. It computes the PSD values, extracts the data at your specified frequency band, logs the values to `data/psdPr/`, and simultaneously pipes the extracted stream to your designated Graphite server!

**Example Output (data/psdPr):**
```
2023-01-29  01:00:00    -57
2023-01-29  01:30:00    -57
2023-01-29  02:00:00    -57
2023-01-29  02:30:00    -56
```

## 📚 Acknowledgments
* Original codebase derived from the [IRIS DMC Noise Toolkit](https://github.com/iris-edu/noise-toolkit).
* Early modifications to support the Berkeley Seismology Lab were made by Sylvester Seo.
* Later modernization, bug fixes, automated Graphite telemetry scaling, and software refactoring contributed by Matthew Ju (@matthewju).