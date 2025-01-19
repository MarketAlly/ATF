# ATF Service Tools

This directory contains tools for managing, generating, validating, and analyzing ATF (Algorithmic Transparency Feed) files.

## Directory Structure
```
tools/
├── feed-generator/
│   └── generator.py      # Feed generation tool
├── feed-reader/
│   └── reader.py         # Feed parsing and analysis
├── feed-manager/
│   ├── manager.py        # Feed management utilities
│   └── impact_templates.json  # Impact assessment templates
└── validator/
    ├── validator.py      # Feed validation tool
    └── tests/            # Validator tests
        └── test_files/   # Test data
```

## Feed Generator

Generate ATF-compliant feed files from various data sources.

### Usage
```bash
python generator.py --config config.json --output feed.xml
```

### Features
- Template-based generation
- Batch processing
- Customizable formats
- Schema compliance
- Validation integration

## Feed Reader

Parse and analyze ATF feed files.

### Usage
```bash
python reader.py feed.xml [--format json|text]
```

### Features
- Multiple output formats
- Statistical analysis
- Content verification
- Metric extraction
- Historical analysis

## Feed Manager

Manage feed lifecycles, versions, and impact assessments.

### Usage
```bash
# Archive a feed
python manager.py --workspace /path/to/workspace archive feed.xml 1.0.0

# Compare feeds
python manager.py --workspace /path/to/workspace compare old.xml new.xml

# Automated update
python manager.py --workspace /path/to/workspace update feed.xml updates.json 1.0.1
```

### Features
1. Feed Archiving
   - Version tracking
   - Metadata storage
   - Checksums
   - Search capabilities

2. Version Control
   - Git integration
   - Change history
   - Rollback support
   - Branch management

3. Impact Assessments
   - Template-based generation
   - Risk analysis
   - Metric tracking
   - Compliance checking

4. Feed Comparison
   - Structural diff
   - Content analysis
   - Change highlighting
   - Impact evaluation

## Validator

Validate ATF files against the schema and specification.

### Usage
```bash
python validator.py feed.xml [--schema schema.xsd]
```

### Features
- XML Schema validation
- Semantic validation
- Best practice checks
- Error reporting
- Batch validation

## Common Tasks

1. Create a new feed:
```bash
python generator.py --template basic --data input.json --output feed.xml
```

2. Validate and analyze:
```bash
python validator.py feed.xml && python reader.py feed.xml
```

3. Archive and version:
```bash
python manager.py archive feed.xml 1.0.0
```

4. Generate impact assessment:
```bash
python manager.py impact-assessment --template algorithm_update data.json
```

## Development

1. Setup environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest validator/tests/
```

3. Format code:
```bash
black .
```

## Contributing

1. Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Include tests

2. Testing
- Write unit tests
- Add test data
- Test edge cases
- Verify validation

3. Documentation
- Update README
- Add examples
- Document APIs
- Note changes