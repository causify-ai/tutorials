# Timestamp Format Guide

## Standard Format

In this Bitcoin forecasting application, we use the ISO8601 format with 'T' separator as the standard timestamp format:

```
YYYY-MM-DDThh:mm:ss
```

Example: `2025-05-14T03:51:35`

This format is used consistently across:
- Raw data files
- Prediction files
- Metrics files
- Dashboard display

## Common Issues

### Timestamp Format Mismatch

The application may encounter issues when different parts of the system use different timestamp formats:

1. **Space Separator vs T Separator**: 
   - Correct: `2025-05-14T03:51:35`
   - Incorrect: `2025-05-14 03:51:35`

2. **Date Mismatch**:
   - When prediction timestamps are from a different date than the actual data
   - Example: Predictions from `2025-05-08` but actual data from `2025-05-14`

3. **Time Zone Issues**:
   - All timestamps should be in UTC
   - Different time zones can cause comparison failures

### Dashboard Error: 'str' object has no attribute 'date'

This error occurs when:
1. Timestamps are stored as strings in one dataset and datetime objects in another
2. The code tries to call `.date()` on a string timestamp

## How to Fix Timestamp Issues

### Using the Timestamp Utility Functions

The application includes utility functions in `utilities/timestamp_format.py`:

```python
# Parse any timestamp format to datetime
parsed_dt = parse_timestamp("2025-05-14T03:51:35")

# Format datetime to ISO8601 with T separator
formatted_ts = format_timestamp(datetime_obj, use_t_separator=True)
```

### Using the Fix Timestamps Script

We provide a script to fix timestamp format issues in prediction files:

```bash
# Fix timestamps to today's date
./scripts/fix_timestamps.sh

# Fix timestamps to a specific date
./scripts/fix_timestamps.sh 2025-05-14
```

The script:
1. Updates the dates in prediction files to the specified date
2. Maintains the original time components
3. Ensures all timestamps use the ISO8601 format with T separator
4. Creates backups of the original files

## Best Practices

1. Always use the `format_timestamp()` utility when saving timestamps to files
2. Use `parse_timestamp()` when reading timestamps from any source
3. Run the fix_timestamps script if you notice date mismatches in the dashboard
4. When comparing timestamps, ensure both are datetime objects using `pd.to_datetime()`

## Technical Implementation

The application uses the following approach for timestamp handling:

1. **Data Collection**: Timestamps are recorded in ISO8601 format with T separator
2. **Prediction Generation**: Timestamps are formatted using the same standard
3. **Dashboard Display**: Timestamps are parsed to datetime objects for comparison
4. **Charts**: Dual-axis plotting is used when timestamps don't match exactly 