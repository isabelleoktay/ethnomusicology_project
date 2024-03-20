# extract_score_data.py

from music21 import *
import os

def get_score_data(scores_folder, folder_path, annotations):
    """
    Process score files and annotations to extract relevant information.

    This function takes a list of score file names, the folder path containing the score files,
    and annotations as input. It iterates over each file in the score folder, parses the file,
    extracts relevant information based on the annotations, and stores the information in a dictionary.

    Parameters:
        SCORES_FOLDER (list): A list of score file names.
        FOLDER_PATH (str): The path to the folder containing the score files.
        annotations (list): A list of annotations containing information about score sections.

    Returns:
        dict: A dictionary containing information extracted from the score files and annotations.
    """
    scores = {}

    for file_name in scores_folder:
        mbid = file_name.split('.xml')[0]
        file_path = os.path.join(folder_path, file_name)  

        try:
            for annotation in annotations:
                if annotation['mbid'] == mbid:
                    score = converter.parse(file_path)
                    scores[mbid] = {'score': score, 'annotations': annotation['sections']}
                    break

        except Exception as e:
            print(f"Error parsing file '{file_path}': {e}")

    return scores


def parse_score_info(score_info):
    """
    Parse score information dictionary and extract score and annotations.

    Parameters:
        score_info (dict): A dictionary containing information about the score.

    Returns:
        score (object): The music21 Score object.
        annotations (list): A list of annotations associated with the score.
    """
    return score_info['score'], score_info['annotations']


def extract_measures(score, start_offset, end_offset):
    '''
    Extracts a part of a music score between specified start and end offsets.

    PARAMETERS:
        score (music21.stream.Score): The music score from which to extract measures.
        start_offset (float): The starting offset of the extraction (in beats).
        end_offset (float): The ending offset of the extraction (in beats).

    RETURNS:
        extracted_part (music21.stream.Stream): The extracted part of the score between
            the specified start and end offsets.
    '''
    extracted_part = stream.Stream()

    for element in score.getElementsByOffset(start_offset, end_offset, includeEndBoundary=False):
        extracted_part.append(element)

    return extracted_part


def extract_sections(score, score_sections):
    '''
    Extracts sections of music scores based on provided start and end measures.

    PARAMETERS:
        score (music21.stream.Score): The music score from which sections will be extracted.
        score_sections (list): A list of dictionaries specifying the sections to be extracted.
            Each dictionary should contain the following keys:
                - 'start': The starting measure of the section.
                - 'end': The ending measure of the section.
                - Optionally, if the section contains subsections (e.g., sanai), they can be specified.

    RETURNS:
        score_sections (list): A list of dictionaries containing the extracted sections.
            Each dictionary will now contain an additional key-value pair:
                - 'score': The extracted section as a music21.stream.Score object.
            If the sections contain subsections, they will be recursively extracted and added under 'score' key.
    '''

    for section in score_sections:
        start_measure = section['start']
        end_measure = section['end']

        extracted_measures = extract_measures(score, start_measure, end_measure)
        section['score'] = extracted_measures

        if 'ṣanā`i`' in section:
            sanai = section['ṣanā`i`']
            num_sanai = len(sanai)

            for i in range(num_sanai):
                sana = sanai[i]
                sana_start = sana['start']
                sana_end = sana['end']
                sana_measures = extract_measures(score, sana_start, sana_end)
                section['ṣanā`i`'][i]['score'] = sana_measures

                if 'lines' in sana:
                    lines = sana['lines']
                    num_lines = len(lines)

                    for j in range(num_lines):
                        line = lines[j]
                        line_start = line['start']
                        line_end = line['end']
                        line_measures = extract_measures(score, line_start, line_end)
                        section['ṣanā`i`'][i]['lines'][j]['score'] = line_measures

                        if 'sections' in line:
                            line_sections = line['sections']
                            num_line_sections = len(line_sections)

                            for k in range(num_line_sections):
                                line_section = line_sections[k]
                                line_section_start = line_section['start']
                                line_section_end = line_section['end']
                                line_section_measures = extract_measures(score, line_section_start, line_section_end)
                                section['ṣanā`i`'][i]['lines'][j]['sections'][k]['score'] = line_section_measures

    return score_sections


def add_streams_to_score_data(scores_data):
    """
    Add flattened streams to the score data and update annotations.

    This function iterates over each score in the input dictionary 'scores'. For each score, it extracts the score object
    and annotations using the 'parse_score_info' function, then flattens the score to extract individual notes and rests.
    The flattened score and annotations are then passed to the 'extract_sections' function to extract sections.
    Finally, the updated annotations are stored back into the original score data.

    Parameters:
        scores_data (dict): A dictionary containing information about scores, with MBIDs as keys.

    Returns:
        dict: Updated score data with flattened streams and updated annotations.
    """
    for mbid in scores_data:
        score, annotations = parse_score_info(scores_data[mbid])

        flattened_score = score.parts[0].flatten().notesAndRests.stream()
        score_sections = extract_sections(flattened_score, annotations)

        scores_data[mbid]['annotations'] = score_sections
    
    return scores_data


def process_annotations(scores_data):
    """
    Process annotations from a dictionary of scores and extract relevant information.

    Parameters:
        scores_data (dict): A dictionary containing score information.

    Returns:
        all_sanai (list): A list of all 'ṣanā`i`' annotations.
        all_sanai_scores (list): A list of scores for all 'ṣanā`i`' annotations.
        all_sanai_lines_scores (list): A list of scores for all lines within 'ṣanā`i`' annotations.
    """
    all_sanai = []
    all_sanai_scores = []
    all_sanai_lines_scores = []

    for mbid in scores_data:
        score_info = scores_data[mbid]
        annotations = score_info['annotations']

        for section in annotations:
            if 'ṣanā`i`' in section:
                sanai = section['ṣanā`i`']
                all_sanai.extend(sanai)

                sana_count = 0
                for sana in sanai:
                    all_sanai_scores.append(sana['score'])

                    lines = sana['lines']
                    all_lines_scores = []
                    for line in lines:
                        all_lines_scores.append(line['score'])

                    all_sanai_lines_scores.append(all_lines_scores)

    return all_sanai, all_sanai_scores, all_sanai_lines_scores


def calculate_score_section_counts(scores_data):
    """
    Calculate the count of score sections for each piece of music in the provided scores data.

    This function takes a dictionary of scores data as input and calculates the count of score sections
    for each piece of music based on the annotations in the scores data.

    Parameters:
        scores_data (dict): A dictionary containing scores data.

    Returns:
        dict: A dictionary containing the count of score sections for each piece of music.
    """
    score_section_counts = {}
    sanai_count = 0

    for mbid in scores_data:
        _, annotations = parse_score_info(scores_data[mbid])
        counts = {}

        for section in annotations:
            if 'ṣanā`i`' in section:
                sanai_count += 1

                this_sanai = 'sanai_' + str(sanai_count)
                if this_sanai not in counts:
                    counts[this_sanai] = {}

                sana_count = 0
                for sana in section['ṣanā`i`']:
                    sana_count += 1

                    this_sana = 'sana_' + str(sana_count)
                    if this_sana not in counts[this_sanai]:
                        counts[this_sanai][this_sana] = {}

                    line_count = 0
                    for line in sana['lines']:
                        line_count += 1

                        this_line = 'line_' + str(line_count)
                        if this_line not in counts[this_sanai][this_sana]:
                            counts[this_sanai][this_sana][this_line] = {}

                        line_section_count = 0
                        for line_section in line['sections']:
                            line_section_count += 1

                        counts[this_sanai][this_sana][this_line]['section_count'] = line_section_count

                    counts[this_sanai][this_sana]['line_count'] = line_count

                counts[this_sanai]['sana_count'] = sana_count

            counts['sanai_count'] = sanai_count

        score_section_counts[mbid] = counts

    return score_section_counts


def get_mizans_of_scores(scores_data):
    '''
    Extract mizans for each file in the dataset for naming plots.

    PARAMETERS:
        - scores_data (dict): A dictionary containing data for each score file.

    RETURNS:
        scores_mizan_dict (dict): A dictionary mapping each file ID (mbid) to its corresponding set of mizans.
    '''
    scores_mizan_dict = {}

    for mbid, data in scores_data.items():
        annotations = data.get('annotations', [])
        mizans = set(annotation['mīzān'] for annotation in annotations)
        scores_mizan_dict[mbid] = mizans

    return scores_mizan_dict