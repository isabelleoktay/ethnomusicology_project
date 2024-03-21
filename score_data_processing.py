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
        first_quarter_count (int): Number of occurrences of the pattern in the beginning 25% of the given section.
        middle_count (int): Number of occurrences of the pattern in the middle 50% of the given section.
        last_quarter_count (int): Number of occurrences of the pattern in the last 25% of the given section.
    '''
    score_pitch_names = [n.name for n in score.getElementsByClass(note.Note)]
    score_length = len(score_pitch_names)

    # Count occurrences of the pattern in the score
    pattern_count = 0
    first_quarter_count = 0
    last_quarter_count = 0
    for i in range(len(score_pitch_names) - len(pattern) + 1):
        if score_pitch_names[i:i+len(pattern)] == pattern:
            pattern_count += 1
            if i < int(score_length * 0.25):
                first_quarter_count += 1
            elif i >= (score_length - int(score_length * 0.25)):
                last_quarter_count += 1

    # Count how prealent a pattern is in the middle 50% of the score section 
    middle_count = pattern_count - (first_quarter_count + last_quarter_count)

    return first_quarter_count, middle_count, last_quarter_count


def count_all_patterns(score, patterns, pattern_counter):
    '''
    Iterate through all the different patterns (centos) of a score to count their prevalence.

    PARAMETERS: 
        - score (music21.stream.Stream): A music21 Stream object representing the score.
        - patterns (list of list of str): A list containing all centos/patterns as lists of pitch names.
        - pattern_counter (function): A function that determines how to segment and count centos for each score

    RETURNS:    
        pattern_counts (dict): A dictionary containing the counts of each pattern.
    '''
    pattern_counts = {}

    for pattern in patterns:
        pattern_str = ''.join(pattern)
        pattern_count = pattern_counter(score, pattern)

        pattern_counts[pattern_str] = pattern_count

    return pattern_counts

def count_all_patterns_wrapper(scores, patterns, pattern_counter):
    '''
    Count all centos in a pattern array from the score sections.

    PARAMETERS: 
        - scores (dict): A dictionary where keys are identifiers for scores and values are music21 Stream objects representing the scores.
        - patterns (list of list of str): A list containing all centos/patterns as lists of pitch names.
        - pattern_counter (function): A function that determines how to segment and count centos for each score
    
    RETURNS:   
        all_centos_counts (dict): A dictionary containing the centos counts for each score, section, sana, and line.

    '''
    all_centos_counts = {}

    for mbid in scores:
        _, annotations = parse_score_info(scores[mbid])
        all_centos_counts[mbid] = {'sanai': {}, 'lines': {}}

        section_count = 0
        for section in annotations:
            section_count += 1

            if 'ṣanā`i`' in section:
                
                sana_count = 0
                for sana in section['ṣanā`i`']:
                    sana_count += 1
                    sana_score = sana['score']

                    which_sana = 'section_' + str(section_count) + '_sana_' + str(sana_count)
                    sana_pattern_counts = count_all_patterns(sana_score, patterns, pattern_counter)
                    all_centos_counts[mbid]['sanai'][which_sana] = sana_pattern_counts

                    line_count = 0
                    for line in sana['lines']:
                        line_count += 1
                        line_score = line['score']

                        which_line = which_sana + '_line_' + str(line_count)
                        line_pattern_counts = count_all_patterns(line_score, patterns, pattern_counter)
                        all_centos_counts[mbid]['lines'][which_line] = line_pattern_counts

    return all_centos_counts


def count_centos_positions(centos_counts_dict):
    '''
    Function used to count the start, middle, and end positions of extracted centos counts for a given set of key centos of ṭab al-māya.

    PARAMETERS: 
        - centos_counts_dict (dict): dict containing the counts for different cetos values

    RETURNS: 
        DataFrame containing counts for start, middle, and end positions of centos.
    '''
    pattern_counts = {'Pattern': [], 'Start': [], 'Middle': [], 'End': []}
    for section, patterns in centos_counts_dict.items():
        for pattern, counts in patterns.items():
            pattern_counts['Pattern'].append(pattern)
            pattern_counts['Start'].append(counts[0])
            pattern_counts['Middle'].append(counts[1])
            pattern_counts['End'].append(counts[2])

    df = pd.DataFrame(pattern_counts)

    # Group by 'Pattern' and sum the counts
    df = df.groupby('Pattern').sum().reset_index()

    # Calculate cumulative counts for each position in the tuple
    df['Start 25%'] = df['Start']
    df['Middle 50%'] = df['Middle']
    df['End 25%'] = df['End']

    # Drop unnecessary columns
    df.drop(['Start', 'Middle', 'End'], axis=1, inplace=True)

    return df


def count_distribution_over_dataset(cumulative_centos_positions):
    '''
    Merge the count distribution data over the dataset.

    This function takes a dictionary of DataFrames containing count distribution data for different centos types 
    and merges the data for the same centos count type. It then aggregates the numerical values for each letter pattern.

    PARAMETERS:
    - cumulative_centos_positions (dict): A dictionary where keys represent centos count types and values are DataFrames
                                          containing count distribution data.

    RETRUNS:
    dict: A dictionary where keys are centos count types and values are DataFrames containing merged and aggregated
          count distribution data for each letter pattern.
    '''
    merged_data = {}
    for key, df in cumulative_centos_positions.items():
        prefix = key.split(':')[0].strip()
        if prefix not in merged_data:
            merged_data[prefix] = df
        else:
            merged_data[prefix] = pd.concat([merged_data[prefix], df], ignore_index=True)

    # Group by 'Pattern' and aggregate numerical values
    for prefix, df in merged_data.items():
        merged_data[prefix] = df.groupby('Pattern').sum().reset_index()

    return merged_data


def get_centos_counts_per_tab_mizan_score(centos_counts, scores_mizan_dict, centos_positions_counter, centos_list_names = CENTOS_LIST_NAMES):
    '''
    Process centos counts data for visualization.

    PARAMETERS:
        - centos_counts (list): A list containing dictionaries of centos counts data.
        - scores_mizan_dict (dict): A dictionary containing mizans for each file in the dataset.

    RETURNS:
        cumulative_sanai_centos_positions (dict): A dictionary containing cumulative counts of centos positions at the sanai level.
        cumulative_line_centos_positions (dict): A dictionary containing cumulative counts of centos positions at the line level.
    '''
    cumulative_sanai_centos_positions = {}
    cumulative_line_centos_positions = {}

    for i, centos_list in enumerate(centos_counts):
        for mbid, count_data in centos_list.items():
            # construct title of tab for graphs
            mizan_values = [mizan for mizan in scores_mizan_dict[mbid] if mizan != 'none']
            tab_mizan_name = 'ṭab‘ al-māya ' + ''.join(str(mizan) for mizan in mizan_values)

            # cumulative counts and graphs (optional) for sanai level
            sanai_centos_counts_dict = count_data.get('sanai', {})
            plot_title = centos_list_names[i] + ': sanai of ' + tab_mizan_name 
            sanai_centos_position_counts_df = centos_positions_counter(sanai_centos_counts_dict)
            cumulative_sanai_centos_positions[plot_title] = sanai_centos_position_counts_df
            #plot_centos_distribution(sanai_centos_position_counts_df, plot_title)

            # cumulative counts and graphs (optional) for line level
            line_centos_counts_dict = count_data.get('lines', {})
            plot_title = centos_list_names[i] + ': lines of ' + tab_mizan_name 
            line_centos_position_counts_df = centos_positions_counter(line_centos_counts_dict)
            cumulative_line_centos_positions[plot_title] = line_centos_position_counts_df
            # plot_centos_distribution(line_centos_position_counts_df, plot_title)

    return cumulative_sanai_centos_positions, cumulative_line_centos_positions


def combine_normalized_position_counts(scores_data):
    '''
    Combine the normalized counts for start, middle, and end positions across all patterns and centos types.

    Parameters:
        data (dict): A dictionary containing centos types as keys and their corresponding dataframes as values.
                     Each dataframe should have columns 'Pattern', 'Start 25%', 'Middle 50%', and 'End 25%'.

    Returns:
        dict: A dictionary containing the combined normalized counts for start, middle, and end positions.
    '''
    # Initialize total normalized counts for start, middle, and end positions
    total_counts = {'Start 25%': 0, 'Middle 50%': 0, 'End 25%': 0}

    # Iterate through the data dictionary and sum normalized counts for each position
    for df in scores_data.values():
        # Normalize counts within each row
        row_sums = df[['Start 25%', 'Middle 50%', 'End 25%']].sum(axis=1)
        normalized_counts = df[['Start 25%', 'Middle 50%', 'End 25%']].div(row_sums, axis=0)

        # Sum normalized counts for each position
        total_counts['Start 25%'] += normalized_counts['Start 25%'].sum()
        total_counts['Middle 50%'] += normalized_counts['Middle 50%'].sum()
        total_counts['End 25%'] += normalized_counts['End 25%'].sum()

    return total_counts