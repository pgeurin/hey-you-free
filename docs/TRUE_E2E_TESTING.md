# True End-to-End Testing Guide

This document describes the comprehensive end-to-end testing approach for the Meeting Scheduler application, focusing on real API calls with seeded data and fixed timestamps.

## Overview

The true end-to-end tests go beyond mocked API calls to test the complete workflow with:
- **Real API calls** to Google Gemini AI
- **Seeded data** for deterministic results
- **Fixed timestamps** for consistent testing
- **Comprehensive validation** of all components

## Test Files

### 1. `test_true_end_to_end.py`
Main end-to-end test suite with real API integration.

**Key Features:**
- Real Gemini API calls (when API key is available)
- Seeded calendar data with fixed timestamps
- Deterministic AI responses using seeds
- Complete workflow testing from data loading to output generation
- Graceful handling of missing API keys

**Test Categories:**
- Calendar data loading and formatting
- AI prompt generation
- Real API calls (deterministic and creative)
- Complete workflow integration
- Error handling and validation
- Reproducibility testing

### 2. `test_seeded_api_demo.py`
Demonstration of seeded API functionality with mocked responses.

**Key Features:**
- Shows how seeded API calls work
- Demonstrates deterministic behavior
- Validates response formats
- Educational examples for understanding the system

### 3. `run_true_e2e_test.py`
Test runner script with environment checking and multiple test modes.

**Features:**
- Environment validation
- Multiple test execution modes
- Clear output and error reporting
- Integration with pytest

## Setup and Usage

### Prerequisites

1. **Environment Setup:**
   ```bash
   mamba activate butterfly
   ```

2. **API Key (Optional):**
   ```bash
   export GOOGLE_API_KEY='your_api_key_here'
   ```
   - Tests will skip API-dependent tests if not set
   - All core functionality tests will still run

### Running Tests

#### Option 1: Using the Test Runner (Recommended)
```bash
python run_true_e2e_test.py
```

Choose from:
- Run with pytest (recommended)
- Run individual test suite
- Both

#### Option 2: Direct pytest
```bash
# Run all end-to-end tests
python -m pytest tests/test_true_end_to_end.py -v

# Run seeded API demo
python -m pytest tests/test_seeded_api_demo.py -v

# Run both
python -m pytest tests/test_true_end_to_end.py tests/test_seeded_api_demo.py -v
```

#### Option 3: Individual Test Suite
```bash
PYTHONPATH=. python tests/test_true_end_to_end.py
PYTHONPATH=. python tests/test_seeded_api_demo.py
```

## Test Architecture

### Seeded Data Approach

The tests use **fixed timestamps** and **seeded API calls** to ensure reproducibility:

```python
# Fixed test date for consistent results
self.test_date = datetime(2025, 1, 15, 10, 0, 0)

# Seeded API calls for deterministic responses
response = get_deterministic_meeting_suggestions(prompt, seed=42)
```

### Calendar Data Structure

Tests use realistic calendar data with fixed timestamps:

```python
phil_events = [
    {
        "kind": "calendar#event",
        "summary": "Morning Standup",
        "start": {"dateTime": "2025-01-16T09:00:00Z"},
        "location": "Office",
        "description": "Daily team sync"
    },
    # ... more events
]
```

### API Response Validation

All API responses are validated against a strict schema:

```python
required_fields = ["date", "time", "duration", "reasoning", 
                  "phil_energy", "chris_energy", "meeting_type"]
```

## Test Scenarios

### 1. Data Loading and Formatting
- Load calendar data from JSON files
- Format events for AI analysis
- Handle invalid data gracefully
- Validate data structure

### 2. AI Prompt Generation
- Create comprehensive prompts
- Include current date context
- Format calendar data properly
- Validate prompt structure

### 3. Real API Integration
- **Deterministic calls** with fixed seeds
- **Creative calls** with higher temperature
- **Reproducibility testing** with same seeds
- **Variation testing** with different seeds

### 4. Complete Workflow
- End-to-end data flow
- File I/O operations
- Error handling
- Output validation

### 5. Error Handling
- Missing API keys
- Invalid responses
- Network failures
- Data validation errors

## Key Benefits

### 1. Deterministic Testing
- Same seeds produce identical results
- Fixed timestamps ensure consistent prompts
- Reproducible test outcomes

### 2. Real API Integration
- Tests actual API behavior
- Validates real response formats
- Catches integration issues

### 3. Comprehensive Coverage
- Tests all components together
- Validates complete workflows
- Ensures system reliability

### 4. Educational Value
- Shows how seeded APIs work
- Demonstrates best practices
- Provides clear examples

## Example Output

### Successful Test Run
```
🚀 RUNNING TRUE END-TO-END TEST SUITE
================================================================================
📝 Note: Some tests require GOOGLE_API_KEY environment variable
================================================================================

🔍 TESTING: Calendar Data Loading
✅ Calendar data loaded successfully
   Phil events: 5
   Chris events: 5

🔍 TESTING: Event Formatting for AI
✅ Event formatting successful
   Phil formatted length: 428 chars
   Chris formatted length: 406 chars

🔍 TESTING: AI Prompt Generation
✅ AI prompt generation successful
   Prompt length: 4357 characters
   Contains current date: 2025-09-05

⚠️  Skipping API tests - GOOGLE_API_KEY not set

🔍 TESTING: Error Handling Without API Key
✅ Error handling without API key works correctly

🔍 TESTING: Validation with Real AI Response Format
✅ Validation with realistic AI response successful
   Validated 3 suggestions

================================================================================
🎯 TRUE END-TO-END TEST SUITE COMPLETE
================================================================================
```

### With API Key
```
🔍 TESTING: Real Gemini API Call (Deterministic)
✅ Real Gemini API call successful
   Generated 3 suggestions
   First suggestion: 2025-01-20 at 15:30

🔍 TESTING: Complete Workflow with Real APIs
✅ Complete workflow successful
   Generated 3 suggestions
   Files saved: /tmp/output/meeting_prompt.txt, /tmp/output/meeting_suggestions.json
```

## Troubleshooting

### Common Issues

1. **Module Import Errors:**
   ```bash
   # Use PYTHONPATH
   PYTHONPATH=. python tests/test_true_end_to_end.py
   ```

2. **Environment Not Active:**
   ```bash
   mamba activate butterfly
   ```

3. **API Key Issues:**
   - Tests will skip API-dependent tests if key is missing
   - Check key format and permissions
   - Verify environment variable is set

4. **Test Failures:**
   - Check environment setup
   - Verify all dependencies are installed
   - Review error messages for specific issues

### Debug Mode

Run tests with verbose output:
```bash
python -m pytest tests/test_true_end_to_end.py -v -s
```

## Best Practices

### 1. Test Data Management
- Use fixed timestamps for consistency
- Create realistic but controlled data
- Include edge cases and error scenarios

### 2. API Testing
- Use seeds for deterministic results
- Test both deterministic and creative modes
- Validate all response formats

### 3. Error Handling
- Test with and without API keys
- Validate error messages
- Ensure graceful degradation

### 4. Documentation
- Document test scenarios clearly
- Include example outputs
- Provide troubleshooting guides

## Integration with CI/CD

The tests are designed to work in CI/CD environments:

- **Without API key:** Core functionality tests run
- **With API key:** Full integration tests run
- **Deterministic:** Same results every time
- **Fast:** Optimized for quick feedback

## Future Enhancements

1. **Performance Testing:** Add timing measurements
2. **Load Testing:** Test with larger datasets
3. **Integration Testing:** Test with real Google Calendar API
4. **Visual Testing:** Add screenshot comparisons
5. **Monitoring:** Add test result tracking

---

This testing approach ensures the Meeting Scheduler application is robust, reliable, and ready for production use.
