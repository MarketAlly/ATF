import pytest
from pathlib import Path
from datetime import datetime, timedelta
from lxml import etree
from validator import ATFValidator, ValidationError

# Fixtures for test setup
@pytest.fixture
def test_files_dir():
    return Path(__file__).parent / 'test_files'

@pytest.fixture
def validator(test_files_dir):
    schema_path = test_files_dir / 'test_schema.xsd'
    return ATFValidator(schema_path)

@pytest.fixture
def base_xml_template():
    """Base XML template for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com/feed</link>
    <description>Test Description</description>
    <lastBuildDate>{lastBuildDate}</lastBuildDate>
    <language>{language}</language>
  </channel>
  {items}
</atf>'''

@pytest.fixture
def base_item_template():
    """Base item template for testing."""
    return '''
  <item>
    <title>Test Item</title>
    <link>https://example.com/item1</link>
    <pubDate>{pubDate}</pubDate>
    <categories>
      <category>{category}</category>
    </categories>
    <description>Test description</description>
    <impactAssessment>
      <summary>Test impact</summary>
      <affectedUsers>{affectedUsers}</affectedUsers>
      <metrics>
        {metrics}
      </metrics>
    </impactAssessment>
  </item>'''

# Date Format Tests
class TestDateValidation:
    def test_valid_date_formats(self, tmp_path, validator, base_xml_template):
        """Test various valid date formats."""
        current_time = datetime.utcnow()
        dates = [
            current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            (current_time - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            (current_time - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
        ]
        
        for date in dates:
            xml = base_xml_template.format(
                lastBuildDate=date,
                language="en-us",
                items=""
            )
            xml_file = tmp_path / "test.xml"
            xml_file.write_text(xml)
            errors = validator.validate_file(xml_file)
            assert not errors, f"Valid date {date} should not produce errors"

    def test_invalid_date_formats(self, tmp_path, validator, base_xml_template):
        """Test various invalid date formats."""
        invalid_dates = [
            "2025-01-19",  # Missing time
            "2025-01-19T12:00",  # Missing seconds
            "2025-01-19 12:00:00",  # Wrong separator
            "2025-13-19T12:00:00Z",  # Invalid month
            "2025-01-32T12:00:00Z",  # Invalid day
            "2025-01-19T25:00:00Z",  # Invalid hour
            datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),  # Missing Z
            (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")  # Future date
        ]
        
        for date in invalid_dates:
            xml = base_xml_template.format(
                lastBuildDate=date,
                language="en-us",
                items=""
            )
            xml_file = tmp_path / "test.xml"
            xml_file.write_text(xml)
            errors = validator.validate_file(xml_file)
            assert errors, f"Invalid date {date} should produce errors"

# Language Code Tests
class TestLanguageValidation:
    def test_valid_language_codes(self, tmp_path, validator, base_xml_template):
        """Test all supported language codes."""
        for lang in validator.ALLOWED_LANGUAGES:
            xml = base_xml_template.format(
                lastBuildDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                language=lang,
                items=""
            )
            xml_file = tmp_path / "test.xml"
            xml_file.write_text(xml)
            errors = validator.validate_file(xml_file)
            assert not errors, f"Valid language code {lang} should not produce errors"

    def test_invalid_language_codes(self, tmp_path, validator, base_xml_template):
        """Test various invalid language codes."""
        invalid_langs = [
            "eng",  # Wrong format
            "en_US",  # Wrong separator
            "en-USA",  # Wrong region format
            "xx-xx",  # Non-existent code
            "",  # Empty
            "12345"  # Invalid format
        ]
        
        for lang in invalid_langs:
            xml = base_xml_template.format(
                lastBuildDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                language=lang,
                items=""
            )
            xml_file = tmp_path / "test.xml"
            xml_file.write_text(xml)
            errors = validator.validate_file(xml_file)
            assert errors, f"Invalid language code {lang} should produce errors"

# Metric Format Tests
class TestMetricValidation:
    @pytest.fixture
    def metric_template(self):
        return '<metric name="{name}">{value}</metric>'

    def test_valid_metric_formats(self, tmp_path, validator, base_xml_template, base_item_template, metric_template):
        """Test various valid metric formats."""
        valid_metrics = [
            ("Percentage", "+10.5%"),
            ("Ratio", "3:1"),
            ("Duration", "200ms"),
            ("Duration", "1.5s"),
            ("Duration", "30min"),
            ("Boolean", "true"),
            ("Numeric", "-15.7"),
            ("Numeric", "+42")
        ]
        
        for name, value in valid_metrics:
            metric = metric_template.format(name=name, value=value)
            item = base_item_template.format(
                pubDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                category="Test",
                affectedUsers="10%",
                metrics=metric
            )
            xml = base_xml_template.format(
                lastBuildDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                language="en-us",
                items=item
            )
            xml_file = tmp_path / "test.xml"
            xml_file.write_text(xml)
            errors = validator.validate_file(xml_file)
            assert not errors, f"Valid metric {name}={value} should not produce errors"

    def test_invalid_metric_formats(self, tmp_path, validator, base_xml_template, base_item_template, metric_template):
        """Test various invalid metric formats."""
        invalid_metrics = [
            ("Percentage", "10.5"),  # Missing %
            ("Percentage", "10.5%%"),  # Double %
            ("Ratio", "3:"),  # Incomplete ratio
            ("Duration", "200"),  # Missing unit
            ("Duration", "1.5x"),  # Invalid unit
            ("Boolean", "yes"),  # Invalid boolean
            ("Numeric", "15.7.2"),  # Invalid number
            ("Numeric", "++42")  # Invalid format
        ]
        
        for name, value in invalid_metrics:
            metric = metric_template.format(name=name, value=value)
            item = base_item_template.format(
                pubDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                category="Test",
                affectedUsers="10%",
                metrics=metric
            )
            xml = base_xml_template.format(
                lastBuildDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                language="en-us",
                items=item
            )
            xml_file = tmp_path / "test.xml"
            xml_file.write_text(xml)
            errors = validator.validate_file(xml_file)
            assert errors, f"Invalid metric {name}={value} should produce errors"

# Large File Tests
class TestFileSizeValidation:
    def test_large_file_validation(self, tmp_path, validator, base_xml_template, base_item_template):
        """Test validation of large files."""
        # Create a large file by repeating items
        items = ""
        current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Generate enough items to exceed MAX_FEED_SIZE
        while len(items) < validator.MAX_FEED_SIZE:
            items += base_item_template.format(
                pubDate=current_time,
                category="Test",
                affectedUsers="10%",
                metrics='<metric name="test">+10%</metric>'
            )
        
        xml = base_xml_template.format(
            lastBuildDate=current_time,
            language="en-us",
            items=items
        )
        xml_file = tmp_path / "large_test.xml"
        xml_file.write_text(xml)
        
        errors = validator.validate_file(xml_file)
        assert errors, "File exceeding MAX_FEED_SIZE should produce errors"

# Malformed XML Tests
class TestMalformedXML:
    def test_incomplete_xml(self, tmp_path, validator):
        """Test validation of incomplete XML."""
        incomplete_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <channel>
    <title>Test Feed</title>'''
        
        xml_file = tmp_path / "incomplete.xml"
        xml_file.write_text(incomplete_xml)
        errors = validator.validate_file(xml_file)
        assert errors, "Incomplete XML should produce errors"

    def test_missing_required_elements(self, tmp_path, validator):
        """Test validation of XML missing required elements."""
        missing_required = '''<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <channel>
    <title>Test Feed</title>
    <description>Test Description</description>
  </channel>
</atf>'''
        
        xml_file = tmp_path / "missing_required.xml"
        xml_file.write_text(missing_required)
        errors = validator.validate_file(xml_file)
        assert errors, "XML missing required elements should produce errors"

    def test_invalid_characters(self, tmp_path, validator, base_xml_template):
        """Test validation of XML with invalid characters."""
        xml = base_xml_template.format(
            lastBuildDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            language="en-us",
            items=f'<item><title>Test\x00Item</title></item>'
        )
        xml_file = tmp_path / "invalid_chars.xml"
        xml_file.write_text(xml)
        errors = validator.validate_file(xml_file)
        assert errors, "XML with invalid characters should produce errors"

    def test_mismatched_tags(self, tmp_path, validator):
        """Test validation of XML with mismatched tags."""
        mismatched_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://www.algorithmictransparency.gov/atf" version="1.0">
  <channel>
    <title>Test Feed</title>
    </channel2>
</atf>'''
        
        xml_file = tmp_path / "mismatched.xml"
        xml_file.write_text(mismatched_xml)
        errors = validator.validate_file(xml_file)
        assert errors, "XML with mismatched tags should produce errors"

    def test_invalid_namespace(self, tmp_path, validator):
        """Test validation of XML with invalid namespace."""
        invalid_ns_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<atf xmlns="https://invalid.example.com/ns" version="1.0">
  <channel>
    <title>Test Feed</title>
  </channel>
</atf>'''
        
        xml_file = tmp_path / "invalid_ns.xml"
        xml_file.write_text(invalid_ns_xml)
        errors = validator.validate_file(xml_file)
        assert errors, "XML with invalid namespace should produce errors"