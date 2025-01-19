# ATF Validator

A validation tool for Algorithmic Transparency Feed (ATF) files.

## Overview

The ATF validator ensures that your feed files comply with the ATF specification. It performs:
- XML Schema validation
- Date format validation
- URL format validation
- Semantic content validation

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python validator.py path/to/your/feed.xml
```

With custom schema:
```bash
python validator.py --schema path/to/schema.xsd path/to/your/feed.xml
```

## Options

- `--schema`: Specify a custom schema file (default: ../schema/atf-1.0.xsd)
- `--verbose`: Show detailed validation messages
- `--quiet`: Only show errors

## Exit Codes

- 0: Validation successful
- 1: Validation errors found
- 2: System error (e.g., file not found)

## Development

Run tests:
```bash
pytest tests/
```

Run type checking:
```bash
mypy validator.py
```