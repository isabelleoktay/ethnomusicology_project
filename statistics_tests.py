from scipy.stats import chi2_contingency
import pandas as pd

def chi_squared_test(data):
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
        pattern_data = data[data['Pattern'] == pattern][['Start 25%', 'Middle 50%', 'End 25%']].values
        chi2_stat, p_val, dof, ex = chi2_contingency(pattern_data)
        
        # Determine if the result is significant (p-value < 0.05)
        is_significant = p_val < 0.05
        
        chi_results.append({'Pattern': pattern, 'p-value': p_val, 'Significant': is_significant})
    
    return pd.DataFrame(chi_results)


def mcnemar_test(df, significance_val=0.05):
    """
    Perform McNemar's test for paired nominal data.

    This function compares the marginal frequencies of two binary variables measured on the same subjects,
    which represent the occurrences of a pattern in different positions (start 25%, middle 50%, end 25%).

    Parameters:
        - df (DataFrame): DataFrame containing pattern occurrence counts in different positions.

    Returns:
        DataFrame: DataFrame containing p-values for each pattern.
    """
    results = []
    for pattern in df['Pattern']:
        pattern_data = df[df['Pattern'] == pattern][['Start 25%', 'Middle 50%', 'End 25%']].values
        # Perform McNemar's test for adjacent positions
        p_vals = []
        for i in range(2):  # Compare start 25% vs. middle 50%, and middle 50% vs. end 25%
            contingency_table = [[pattern_data[0, i], pattern_data[0, i+1]],
                                 [pattern_data[0, i+1], pattern_data[0, i]]]
            _, p_val, _, _ = chi2_contingency(contingency_table)
            p_vals.append(p_val)
        # Take the maximum p-value among the two comparisons
        max_p_val = max(p_vals)
        # Check if the result is significant
        significant = max_p_val < significance_val
        results.append((max_p_val, significant))

    result_df = df.copy()
    result_df['p-value'] = [res[0] for res in results]
    result_df['Significant'] = [res[1] for res in results]
    return result_df


def count_significance(stat_sig_data):
    '''
    Count the number of True values in the 'Significant' column of each DataFrame in the given dictionary.

    PARAMETERS:
        - stat_sig_data (dict): Dictionary containing statistical test data with DataFrame values having a 'Significant' column.

    RETURNS:
        counts_averages_df (pandas DataFrame): DataFrame containing the count of True values in the 'Significant' column for each DataFrame.
    '''
    counts_averages = {}
    for centos_list, data_frame in stat_sig_data.items():
        true_counts = data_frame['Significant'].sum()
        total_data_points = len(data_frame)
        counts_averages[centos_list] = true_counts / total_data_points

    counts_averages_df = pd.DataFrame(counts_averages.items(), columns=['Centos_List', 'Average_Significance'])
    return counts_averages_df
