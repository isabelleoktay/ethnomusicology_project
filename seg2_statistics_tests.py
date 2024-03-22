from scipy.stats import chi2_contingency
from statsmodels.stats.contingency_tables import cochrans_q
import pandas as pd

def chi_squared_test_10(data):
    """
    Test the statistical significance of pattern occurrence in different positions.

    This function performs the chi-square test for each pattern to determine if there
    is a statistically significant association between the pattern and its occurrence
    in the start 25%, middle 50%, and end 25% positions.

    PARAMETERS:
        - data (dict): A dictionary containing data for different patterns and their occurrence
                   counts in start 25%, middle 50%, and end 25% positions.

    RETURNS:
        pd.DataFrame: A DataFrame containing the chi-square test results for each pattern.
                      It includes columns for Pattern, p-value, and whether the result is significant.
    """
    chi_results = []
    
    for pattern in data['Pattern']:
        pattern_data = data[data['Pattern'] == pattern][['10th Percentile', '20th Percentile', '30th Percentile', \
                       '40th Percentile', '50th Percentile', '60th Percentile', \
                       '70th Percentile', '80th Percentile', '90th Percentile', \
                       '100th Percentile']].values
        chi2_stat, p_val, dof, ex = chi2_contingency(pattern_data)
        
        # Determine if the result is significant (p-value < 0.05)
        is_significant = p_val < 0.05
        
        chi_results.append({'Pattern': pattern, 'p-value': p_val, 'Significant': is_significant})
    
    return pd.DataFrame(chi_results)

def cochrans_q_test(df, significance_val=0.05):
    """
    Performs Cochran's Q test on related samples.

    Parameters:
        df (DataFrame): DataFrame containing counts/frequencies of patterns across related samples.
                        Each row represents a sample/position, and each column represents a pattern.
                        It should have a 'Pattern' column.
        significance_val (float): Significance level for the test (default: 0.05).

    Returns:
        DataFrame: Cochran's Q statistic, p-value, degrees of freedom, and significance.
                   The test is significant if p-value < significance_val.
    """
    only_counts = df.drop(columns=['Pattern'])
    result_tuple = cochrans_q(only_counts, return_object=False)

    # Convert tuple to a list of lists
    data = [list(result_tuple)]
    columns = ['q_stat', 'pvalue', 'deg_f']

    # Create DataFrame
    result_df = pd.DataFrame(data, columns=columns)

    # Add a column indicating if the p-value is less than the significance value
    result_df['Significance'] = result_df['pvalue'] < significance_val

    return result_df

