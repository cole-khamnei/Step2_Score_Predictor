import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import constants

def identify_outliers(values, m = 3.5):
    """"""
    d = np.abs(values - np.nanmedian(values))
    mdev = np.nanmedian(d)
    s = d / mdev
    return s < m

def get_score_df(cleaned_comments):
    """ """
    df = pd.concat([pd.DataFrame(SC.scores, index=[i]) for i, SC in enumerate(cleaned_comments)])
    return df.loc[~df["step 2"].isna()]


def degree_type_dist_plot(data):
    """ """
    fig, ax = plt.subplots(figsize=(10, 4))
    for degree, df in data.groupby(by="status"):
        sns.kdeplot(data=df, x="step 2", fill=True, bw_method=0.3, label=degree + f" (N = {len(df)})")

    ax.set_xlabel("Step 2 Score")
    ax.legend(title="Degree Type")
    ax.set_title("Degree Type Step 2 Score Distributions")
    fig.savefig(os.path.join(constants.PLOT_PATH, "degree_distributions.png"))


def score_dist_plot(data):
    """ """
    nonnan_step_scores = data["step 2"].loc[~data["step 2"].isna()]
    y = np.bincount(nonnan_step_scores)
    x = np.arange(len(y))

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(x, y / np.sum(y))
    ax.set_xlim(200, 300)
    sns.kdeplot(data=data, x="step 2", fill=True, bw_method=0.2, color="C0", ax=ax)
    ax.set_xlabel("Step 2 Score")
    ax.set_title("Step 2 Score Distributions")
    fig.savefig(os.path.join(constants.PLOT_PATH, "score_distribution.png"))