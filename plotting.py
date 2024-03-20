import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# if no specific plot folder is specified, will make a folder called plots in which they are saved
PLOTS_PATH = 'plots'


def save_plot(plot, plot_title, plots_folder=PLOTS_PATH):
    '''
    Save a plot to a speficied folder with a specified name.

    PARAMETERS: 
        - plot_title (str): plot_title for plot file.
        - plots_folder (str): Folder to save plot file in.
    '''

    file_name = plot_title.replace(' ', '_')

    file_path = os.path.join(plots_folder, file_name)
    plot.savefig(file_path)


def plot_centos_distribution(cumulative_df, plot_title, plots_folder=PLOTS_PATH, save_plot = False):
    '''
    Function used to plot the distribution of extracted centos counts for a given set of key centos of ṭab al-māya.

    PARAMETERS: 
        - cumulative_df (DataFrame): DataFrame containing cumulative counts for start, middle, and end positions of centos.
        - plot_title (str): name for the plot
        - plots_folder (str): folder where to save plots
        - save_plot (bool): choose to save plot file or not to given plots_folder

    OUTPUT: 
        Displays the cumulative graph of centos placement.

    RETURNS:
        nothing
    '''

    # Melt the DataFrame to prepare for graphing
    melted_cumulative_df = pd.melt(cumulative_df, id_vars='Pattern', var_name='Position', value_name='Cumulative Count')

    # Plot cumulative counts
    plt.figure(figsize=(10, 6))
    sns.barplot(data=melted_cumulative_df, x='Pattern', y='Cumulative Count', hue='Position', palette='pastel')
    plt.title('Cumulative Counts of Positions of Centos: ' + plot_title)
    plt.xlabel('Pattern')
    plt.ylabel('Cumulative Count')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Position', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    if save_plot:
        save_plot(plt, plot_title, plots_folder)

    plt.show()


def plot_complete_distribution_trend(total_counts, level, plots_folder=PLOTS_PATH):
    """
    Plot the development of counts for start, middle, and end positions on a line chart.

    Parameters:
        total_counts (dict): A dictionary containing the total counts for start, middle, and end positions.
        level (str): indicate whether plot is on sanai or line level 
        plots_folder (str): path to save plots into
    """

    plot_title = f'Distribution of Centos at the Start, Middle, and End Positions at {level} level'

    # Convert the dictionary to a pandas DataFrame
    df = pd.DataFrame(total_counts, index=[0])

    # Normalize the counts
    df_normalized = df.div(df.sum(axis=1), axis=0)

    # Melt the DataFrame to long format for easier plotting
    df_melted = df_normalized.melt(var_name='Position', value_name='Count')

    # Plot the line chart with smooth curves
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_melted, x='Position', y='Count', marker='o', sort=False, err_style=None, linewidth=3, color='lightblue')
    
    # Fill the area under the line
    x_fill = df_melted['Position'].unique()
    y_fill = df_normalized.values.flatten()
    plt.fill_between(x_fill, y_fill, color='lightblue', alpha=0.3)

    plt.title(plot_title)
    plt.xlabel('Position')
    plt.ylabel('Normalized Count')
    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_plot:
        save_plot(plt, plot_title, plots_folder)

    plt.show()