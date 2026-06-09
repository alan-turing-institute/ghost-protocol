# face_detection

[![Actions Status][actions-badge]][actions-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]



## Installation

```bash
python -m pip install face_detection
```

From source:
```bash
git clone https://github.com/alan-turing-institute/ghost-protocol
cd face_detection
python -m pip install .
```

## Usage

There are two modes depending on where face detection runs.

### Method 1: Detection on host (`detector.py`)

The phone streams raw JPEG frames over TCP; face detection runs on the host machine.

On the host:
```bash
python3 -c "from face_detection.detector import run_tcp_stream; run_tcp_stream('XX.XX.XX.XX', XXXX)"
```

Replace `XX.XX.XX.XX` and `XXXX` with the phone's IP address and port. The phone should be configured to stream JPEG images over TCP. <!-- TODO: DLJ to add docs for this -->

### Method 2: Detection on phone (`detector_phone.py`)

Face detection runs on the phone, which streams the results (coordinates) over TCP. The host receives the face data via a callback.

On the phone, run:
```bash
python3 phone_sender.py
```

On the host:
```bash
python3 -c "from face_detection._detector_phone import run_tcp_coordinate_stream; run_tcp_coordinate_stream(host='XX.XX.XX.XX', port=XXXX, on_face=print)"
```

Replace `XX.XX.XX.XX` and `XXXX` with the phone's IP address and port. The `on_face` callback receives face detection results as they arrive.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on how to contribute.

## License

Distributed under the terms of the [MIT license](LICENSE).


<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/alan-turing-institute/ghost-protocol/workflows/CI/badge.svg
[actions-link]:             https://github.com/alan-turing-institute/ghost-protocol/actions
[pypi-link]:                https://pypi.org/project/face_detection/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/face_detection
[pypi-version]:             https://img.shields.io/pypi/v/face_detection
<!-- prettier-ignore-end -->
