import pytest
from pathlib import Path
from lxml import etree
from validator import ATFValidator

# Fixture for test files directory
@pytest.fixture
def test_files_dir():
    return Path(__file__).parent / 'test_files'

# Fixture for validator instance
@pytest.fixture
def validator(test_files_dir):
    schema_path = test_files_dir / 'test_schema.xsd'
    return ATFValidator(schema_path)

# Sample XML content for testing
@pytest.fixture
def valid_xml():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com/feed</link>
    <description>Test Description</description>
    <lastBuildDate>2025-01-19T12:00:00Z</lastBuildDate>
    <language>en-us</language>
  </channel>
  <item>
    <title>Test Item</title>
    <link>https://example.com/item1</link>
    <pubDate>2025-01-19T10:00:00Z</pubDate>
    <categories>
      <category>Test</category>
    </categories>
    <description>Test item description</description>
    <impactAssessment>
      <summary>Test impact</summary>
      <affectedUsers>10%</affectedUsers>
      <metrics>
        <metric name="test">+10%</metric>
      </metrics>
    </impactAssessment>
  </item>
</atf>'''

@pytest.fixture
def invalid_xml():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <channel>
    <title>Test Feed</title>
    <!-- Missing required elements -->
  </channel>
</atf>'''

def test_validate_valid_xml(tmp_path, validator, valid_xml):
    """Test validation of a valid XML file"""
    xml_file = tmp_path / "valid.xml"
    xml_file.write_text(valid_xml)
    
    errors = validator.validate_file(xml_file)
    assert not errors, "Valid XML should not produce errors"

def test_validate_invalid_xml(tmp_path, validator, invalid_xml):
    """Test validation of an invalid XML file"""
    xml_file = tmp_path / "invalid.xml"
    xml_file.write_text(invalid_xml)
    
    errors = validator.validate_file(xml_file)
    assert errors, "Invalid XML should produce errors"

def test_validate_nonexistent_file(validator):
    """Test validation of a non-existent file"""
    with pytest.raises(FileNotFoundError):
        validator.validate_file("nonexistent.xml")

def test_validate_malformed_xml(tmp_path, validator):
    """Test validation of malformed XML"""
    xml_file = tmp_path / "malformed.xml"
    xml_file.write_text("This is not XML")
    
    errors = validator.validate_file(xml_file)
    assert errors, "Malformed XML should produce errors"

def test_date_validation(validator):
    """Test validation of date formats"""
    test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com/feed</link>
    <description>Test Description</description>
    <lastBuildDate>2025-01-19T12:00:00</lastBuildDate>
    <language>en-us</language>
  </channel>
</atf>'''
    
    doc = etree.fromstring(test_xml.encode())
    errors = validator._validate_dates(etree.ElementTree(doc))
    assert errors, "Invalid date format should produce errors"

def test_uri_validation(validator):
    """Test validation of URI formats"""
    test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <channel>
    <title>Test Feed</title>
    <link>invalid-url</link>
    <description>Test Description</description>
    <lastBuildDate>2025-01-19T12:00:00Z</lastBuildDate>
    <language>en-us</language>
  </channel>
</atf>'''
    
    doc = etree.fromstring(test_xml.encode())
    errors = validator._validate_uris(etree.ElementTree(doc))
    assert errors, "Invalid URI should produce errors"

def test_metrics_validation(validator):
    """Test validation of metrics format"""
    test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com/feed</link>
    <description>Test Description</description>
    <lastBuildDate>2025-01-19T12:00:00Z</lastBuildDate>
    <language>en-us</language>
  </channel>
  <item>
    <title>Test Item</title>
    <link>https://example.com/item1</link>
    <pubDate>2025-01-19T10:00:00Z</pubDate>
    <categories>
      <category>Test</category>
    </categories>
    <description>Test description</description>
    <impactAssessment>
      <summary>Test impact</summary>
      <affectedUsers>invalid-percentage</affectedUsers>
      <metrics>
        <metric name="test">invalid-value</metric>
      </metrics>
    </impactAssessment>
  </item>
</atf>'''
    
    doc = etree.fromstring(test_xml.encode())
    tree = etree.ElementTree(doc)
    
    # Add a custom validation method to test
    errors = []
    for metric in tree.findall(".//metric"):
        if not metric.text.endswith('%'):
            errors.append(f"Invalid metric format: {metric.text}")
    
    assert errors, "Invalid metrics should produce errors"