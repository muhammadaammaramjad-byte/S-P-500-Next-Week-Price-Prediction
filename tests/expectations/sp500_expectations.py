import great_expectations as ge

expectation_suite = {
    "expectations": [
        {"expectation_type": "expect_column_values_to_not_be_null", "kwargs": {"column": "close"}},
        {"expectation_type": "expect_column_values_to_be_between", "kwargs": {"column": "volume", "min_value": 0}},
        {"expectation_type": "expect_column_pair_values_to_be_in_range", "kwargs": {"column_A": "high", "column_B": "low", "max_difference_ratio": 0.5}},
    ]
}

def validate_data(df):
    ge_df = ge.from_pandas(df)
    results = ge_df.validate(expectation_suite)
    assert results["success"], f"Data validation failed: {results['statistics']}"
    return results