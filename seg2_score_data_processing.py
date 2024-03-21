from music21 import *
from extract_score_data import *
import pandas as pd

CENTOS_LIST_NAMES = ['Amin Chachoo centos ', 'TF IDF centos ', 'SIA centos ', 'MGPD centos ']


def count_pattern_in_score(score, pattern):
    '''
    Count occurrences of a single pattern in a single score.

    PARAMETERS: 
        - score (music21.stream.Stream): A music21 Stream object representing the score.
        - pattern (list of str): An array of pitch names representing the pattern to count.

    RETURNS:    
        distributed_pattern_counts: A
    '''
    score_pitch_names = [n.name for n in score.getElementsByClass(note.Note)]
    score_length = len(score_pitch_names)

    # Count occurrences of the pattern in the score
    distributed_pattern_counts = {'10_pct': 0, 
                      '20_pct': 0, 
                      '30_pct': 0,
                      '40_pct': 0,
                      '50_pct': 0,
                      '60_pct': 0,
                      '70_pct': 0,
                      '80_pct': 0,
                      '90_pct': 0,
                      '100_pct': 0}
    for i in range(len(score_pitch_names) - len(pattern) + 1):
        if score_pitch_names[i:i+len(pattern)] == pattern:
            if i < int(score_length * 0.1):
                distributed_pattern_counts['10_pct'] += 1
            elif i >= int(score_length * 0.1) and i < int(score_length * 0.2):
                distributed_pattern_counts['20_pct'] += 1
            elif i >= int(score_length * 0.2) and i < int(score_length * 0.3):
                distributed_pattern_counts['30_pct'] += 1
            elif i >= int(score_length * 0.3) and i < int(score_length * 0.4):
                distributed_pattern_counts['40_pct'] += 1
            elif i >= int(score_length * 0.4) and i < int(score_length * 0.5):
                distributed_pattern_counts['50_pct'] += 1
            elif i >= int(score_length * 0.5) and i < int(score_length * 0.6):
                distributed_pattern_counts['60_pct'] += 1
            elif i >= int(score_length * 0.6) and i < int(score_length * 0.7):
                distributed_pattern_counts['70_pct'] += 1
            elif i >= int(score_length * 0.7) and i < int(score_length * 0.8):
                distributed_pattern_counts['80_pct'] += 1
            elif i >= int(score_length * 0.8) and i < int(score_length * 0.9):
                distributed_pattern_counts['90_pct'] += 1
            elif i >= (score_length - int(score_length * 0.1)):
                distributed_pattern_counts['100_pct'] += 1

    return distributed_pattern_counts


def count_centos_positions(centos_counts_dict):
    '''
    Function used to count the start, middle, and end positions of extracted centos counts for a given set of key centos of ṭab al-māya.

    PARAMETERS: 
        - centos_counts_dict (dict): dict containing the counts for different cetos values

    RETURNS: 
        DataFrame containing counts for 10 percentile positions of centos.
    '''
    pattern_counts = {'Pattern': [], 
                      '10th_Percentile': [], 
                      '20th_Percentile': [], 
                      '30th_Percentile': [],
                      '40th_Percentile': [],
                      '50th_Percentile': [],
                      '60th_Percentile': [],
                      '70th_Percentile': [],
                      '80th_Percentile': [],
                      '90th_Percentile': [],
                      '100th_Percentile': []}
    for section, patterns in centos_counts_dict.items():
        for pattern, percentiles in patterns.items():
            pattern_counts['Pattern'].append(pattern)
            pattern_counts['10th_Percentile'].append(percentiles['10_pct'])
            pattern_counts['20th_Percentile'].append(percentiles['20_pct'])
            pattern_counts['30th_Percentile'].append(percentiles['30_pct'])
            pattern_counts['40th_Percentile'].append(percentiles['40_pct'])
            pattern_counts['50th_Percentile'].append(percentiles['50_pct'])
            pattern_counts['60th_Percentile'].append(percentiles['60_pct'])
            pattern_counts['70th_Percentile'].append(percentiles['70_pct'])
            pattern_counts['80th_Percentile'].append(percentiles['80_pct'])
            pattern_counts['90th_Percentile'].append(percentiles['90_pct'])
            pattern_counts['100th_Percentile'].append(percentiles['100_pct'])

    df = pd.DataFrame(pattern_counts)

    # Group by 'Pattern' and sum the counts
    df = df.groupby('Pattern').sum().reset_index()

    # Calculate cumulative counts for each position in the tuple
    df['10th Percentile'] = df['10th_Percentile']
    df['20th Percentile'] = df['20th_Percentile']
    df['30th Percentile'] = df['30th_Percentile']
    df['40th Percentile'] = df['40th_Percentile']
    df['50th Percentile'] = df['50th_Percentile']
    df['60th Percentile'] = df['60th_Percentile']
    df['70th Percentile'] = df['70th_Percentile']
    df['80th Percentile'] = df['80th_Percentile']
    df['90th Percentile'] = df['90th_Percentile']
    df['100th Percentile'] = df['100th_Percentile']

    # Drop unnecessary columns
    df.drop(['10th_Percentile', '20th_Percentile', '30th_Percentile', \
             '40th_Percentile', '50th_Percentile', '60th_Percentile', \
             '70th_Percentile', '80th_Percentile', '90th_Percentile', \
             '100th_Percentile'], axis=1, inplace=True)

    return df


def combine_normalized_position_counts(scores_data):
    '''
    Combine the normalized counts for 10 percentile positions across all patterns and centos types.

    Parameters:
        data (dict): A dictionary containing centos types as keys and their corresponding dataframes as values.
                     Each dataframe should have columns Pattern, 10th Percentile, 20th Percentile, 30th Percentile,
                     40th Percentile, 50th Percentile, 60th Percentile, 70th Percentile, 80th Percentile, 
                     90th Percentile, and 100th Percentile.

    Returns:
        dict: A dictionary containing the combined normalized counts for the distribution 10 percentiles.
    '''
    # Initialize total normalized counts for start, middle, and end positions
    total_counts = {'10th Percentile': 0, '20th Percentile': 0, '30th Percentile': 0, \
                    '40th Percentile': 0, '50th Percentile': 0, '60th Percentile': 0, \
                    '70th Percentile': 0, '80th Percentile': 0, '90th Percentile': 0, \
                    '100th Percentile': 0}

    # Iterate through the data dictionary and sum normalized counts for each position
    for df in scores_data.values():
        # Normalize counts within each row
        row_sums = df[['10th Percentile', '20th Percentile', '30th Percentile', \
                       '40th Percentile', '50th Percentile', '60th Percentile', \
                       '70th Percentile', '80th Percentile', '90th Percentile', \
                       '100th Percentile']].sum(axis=1)
        normalized_counts = df[['10th Percentile', '20th Percentile', '30th Percentile', \
                       '40th Percentile', '50th Percentile', '60th Percentile', \
                       '70th Percentile', '80th Percentile', '90th Percentile', \
                       '100th Percentile']].div(row_sums, axis=0)

        # Sum normalized counts for each position
        total_counts['10th Percentile'] += normalized_counts['10th Percentile'].sum()
        total_counts['20th Percentile'] += normalized_counts['20th Percentile'].sum()
        total_counts['30th Percentile'] += normalized_counts['30th Percentile'].sum()
        total_counts['40th Percentile'] += normalized_counts['40th Percentile'].sum()
        total_counts['50th Percentile'] += normalized_counts['50th Percentile'].sum()
        total_counts['60th Percentile'] += normalized_counts['60th Percentile'].sum()
        total_counts['70th Percentile'] += normalized_counts['70th Percentile'].sum()
        total_counts['80th Percentile'] += normalized_counts['80th Percentile'].sum()
        total_counts['90th Percentile'] += normalized_counts['90th Percentile'].sum()
        total_counts['100th Percentile'] += normalized_counts['100th Percentile'].sum()

    return total_counts