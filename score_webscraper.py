import praw
import datetime
import numpy as np
import re

import utils
import constants

if utils.is_interactive():
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm


from typing import List, Union
CommentType = praw.models.reddit.comment.Comment

# ------------------------------------------------------------------- #
# --------------------   Reddit API Functions    -------------------- #
# ------------------------------------------------------------------- #

def comment_unravel(com_generator, com_list = None):
    """ """
    if com_list is None:
        com_list = []

    for com in com_generator:
        if isinstance(com, praw.models.reddit.more.MoreComments):
            return comment_unravel(com.comments(), com_list)
        else:
            com_list.append(com)
    
    return com_list


def get_score_comments(CLIENT_ID: str = constants.CLIENT_ID,
                       CLIENT_SECRET: str = constants.CLIENT_SECRET,
                       USER_AGENT: str = constants.USER_AGENT,
                       COMMENT_SAVE_PATH: str = constants.COMMENT_SAVE_PATH,
                       years = [2024, 2023, 2022],
                       limit: int = 200, verbose: bool = False, offline: bool = False) -> List[CommentType]:
    """ """
    # Initialize Reddit API, and then pulls and unravels comments
    try:
        assert not offline
        reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)
    except:
        return utils.pickle_load(COMMENT_SAVE_PATH)
    
    search_text = "title:[score release thread] AND title:([2024] OR [2023])"

    years_str = " OR ".join(f"[{year}]" for year in years)
    search_text = f"title:[score release thread] AND title:({years_str})"
    print(search_text)

    parsed_submissions = []
    for i, submission in enumerate(reddit.subreddit("Step2").search(search_text, limit=limit, sort="new")):
        if verbose:
            print(f"{i:02d}", submission.title, submission.ups)
        if submission.ups > 5:
            parsed_submissions.append(submission)

    comments_all = [com  for sub in tqdm(parsed_submissions, desc="Parsing Threads", unit=" Threads")
                    for com in comment_unravel(sub.comments) if "Test date" in com.body]

    utils.pickle_write(COMMENT_SAVE_PATH, comments_all)

    return comments_all


# ------------------------------------------------------------------- #
# --------------------  Reddit Comment Parsing   -------------------- #
# ------------------------------------------------------------------- #

def str_pair_replace(string, pairs):
    """ """
    for pair in pairs:
        string = string.replace(*pair)
    return string


def remove_substring(string, substrings):
    """ """
    for substring in substrings:
        string = string.replace(substring, "")
    return string


def remove_bracketed_str(string):
    """ """
    new_string = ""
    open_, close_ = False, False
    for c in string:
        if c == "(":
            open_ = True
        elif c == ")":
            open_ = False
        elif not open_:
            new_string += c
    
    return new_string


def remove_regex(string, regex_cmds):
    """ """
    for regex_cmd in regex_cmds:
        found_items = re.findall(regex_cmd, string)
        for item_ in found_items:
            substring = regex_cmd.replace("(\d+)", item_)
            string = remove_substring(string, [substring])
    return string


def get_date(reddit_object):
    """ """
    return datetime.date.fromtimestamp(reddit_object.created_utc)


def parse_comment(comment):
    """ """
    txt_mod_pairs = [("\n\n", "\n"), (" :", ":"), ("  ", " "), ("NBME ", "NBME"),
                     (": ", ":"), (":", ": "), ("*", ""), ("( ", "("), ("%-", "%:"), ("score -", "score:"),
                     ("score ", "score: ")
                    ]
    return str_pair_replace(comment.body, txt_mod_pairs).lower()


def score_range_control(score_key: str, score: Union[float, int]):
    if constants.SCORE_RANGES[score_key][0] <= score <= constants.SCORE_RANGES[score_key][1]:
        return score
    
    return np.nan


def get_score(line, identifier, length=3):
    """ """
    assert identifier in line, line

    score = remove_bracketed_str(line.split(identifier)[1]).strip()
    score = remove_substring(score, '_.\~' + r'"\"').lstrip(": %")[:length]

    try:
        return int(score)
    except:
        return np.nan

    
def get_timing(line: str, score_key: str):
    """"""
    assert score_key in line
    
    try:
        timing = line.split("(")[1].split(")")[0]
        return timing
    except:
        return np.nan

    
def get_degree_status(line: str):
    """ """
    status = line.split("us img status:")[-1]
    status = remove_substring(status, ": ,\r.")
    if status is None:
        return "None"
    
    if "img" in status:
        if "non" in status or "nn" in status:
            return "Non-US IMG MD"
        elif "us" in status:
            return "US IMG MD"
        else:
            return "Non-US IMG MD"

    if "do" in status:
        return "US DO"
    
    if any(c in status for c in ["canadian", "non"]):
        return "Non-US IMG MD"
    
    if "us" in status or "md" in status:
        return "US MD"

    return "None"

# ------------------------------------------------------------------- #
# --------------------  UWorld Percent Parsing   -------------------- #
# ------------------------------------------------------------------- #

DOUBLE_PASS_IDS = ["second", "first", "1st", "2nd", "pass 2"]

def get_uworld_score(line):
    """ """
    assert "uworld % correct:" in line, line

    numbers = [num for num in re.findall('\d+', line) if len(num) == 2 or num == "100"]
    string = line.split("uworld % correct:")[1]
    two_pass_true = any(tk in line for tk in DOUBLE_PASS_IDS)
    line = remove_substring(line, ["2nd", "pass", "first", "1st", "second"])
    string = str_pair_replace(string, [("1st", "first"), ("2nd", "second"),
                                       ("(one", "(first"), ("pass 1", "first"),
                                       ("pass 2", "second"),
                                       ("done", "complete"), ("used", "complete"),
                                       ("like", ""), ("about", ""), ("ish", ""), ("  ", " ")
                                      ])

    score_1, score_2 = np.nan, np.nan
    if len(numbers) <= 1 or not two_pass_true:
        return get_score(line, "uworld % correct", length=2), score_1, score_2
    elif len(numbers) == 2:
        if "first" in string and "second" in string:
            idx = (0, 1) if string.find("first") < string.find("second") else (1, 0)
            score_1, score_2 = (int(numbers[idx[0]]), int(numbers[idx[1]]))

        elif "first" in string:
            score_1 = get_score(line, "uworld % correct", length=2)

        elif "second" in string:
            score_2 = get_score(line, "uworld % correct", length=2)

    elif len(numbers) > 2:

        tks = np.array(["first", "second", "complet"])
        locs = [string.find(s) for s in tks]


        regex_cmds = [r"(\d+)% comp", r"through (\d+)%", r"completed (\d+)%",
                     "(\d+)% of", "did (\d+)%"]
        p_cp = [g for cmd in regex_cmds for g in re.findall(cmd, string)]

        if len(p_cp) > 0:
            c_string = remove_regex(string, regex_cmds)
            score_set = [int(num) for num in re.findall('\d+', c_string) if len(num) == 2] + [np.nan]
            f_p, s_p = (c_string.find("first"), c_string.find("second"))

            if f_p != -1 and s_p != -1:
                idx = (0, 1) if f_p < s_p else (1, 0)
                score_1, score_2 = score_set[idx[0]], score_set[idx[1]]

    scores = [score_1, score_2]
    score = np.nan if all(np.isnan(s) for s in scores) else np.nanmax(scores)
    
    if score < 50:
        return np.nan, np.nan, np.nan
    
    return score, score_1, score_2


class ScoreComment:
    def __init__(self, step_comment: str):
        self.comment = step_comment
        self.date = get_date(self.comment)
        self.clean()
        self.parse_scores()
        self.get_status()

    def __repr__(self):
        print(self.scores)
        return self.comment_clean
    
    def clean(self):
        self.comment_clean = str_pair_replace(self.comment.body, constants.COMMENT_REPLACEMENTS).lower()
        self.comment_clean = str_pair_replace(self.comment_clean, constants.STEP_2_SCORE_REPLACEMENTS)
        return self.comment_clean
    
    def get_status(self):
        self.status = "None"
        for line in self.comment_clean.split("\n"):
            if "status" in line:
                self.status = get_degree_status(line)

        self.scores["status"] = self.status

    def parse_scores(self):
        lines = self.comment_clean.split("\n")
        

        self.scores = {score_key: np.nan for score_key in constants.KEY_ID_PAIRS}
        self.timing = {score_key: np.nan for score_key in constants.KEY_ID_PAIRS}
        
        self.scores["uworld %"] = np.nan
        self.scores["uworld % (pass 1)"] = np.nan
        self.scores["uworld % (pass 2)"] = np.nan
        
        for key, (identifier, length) in constants.KEY_ID_PAIRS.items():
            for line in lines:
                if "uworld % correct:" in line:
                    score, score_1, score_2 = get_uworld_score(line)
                    self.scores["uworld %"] = score
                    self.scores["uworld % (pass 1)"] = score_1
                    self.scores["uworld % (pass 2)"] = score_2
                
                if identifier in line:
                    score = get_score(line, identifier, length=length)
                    timing = get_timing(line, identifier)
                    
                    self.scores[key] = score
                    self.timing[key] = timing
                else:
                    continue

        for key in self.scores.keys():
            lower, upper = constants.SCORE_RANGES[key]
            if self.scores[key] < lower or self.scores[key] > upper:
                self.scores[key] = np.nan

        nbme_scores = np.array([values for key, values in self.scores.items()
                                if key in constants.NBME_SCORE_KEYS and not np.isnan(values)])
        nbme_scores = np.sort(nbme_scores)[::-1]

        if len(nbme_scores) > 0:    
            self.scores["nbme max"] = nbme_scores[0]
            self.scores["nbme max2"] = nbme_scores[1] if len(nbme_scores) > 1 else np.nan
            self.scores["nbme max3"] = nbme_scores[2] if len(nbme_scores) > 2 else np.nan

        else:
            for key in ["nbme max", "nbme max2", "nbme max3"]:
                self.scores[key] = np.nan

        self.scores["nbme range"] = nbme_scores[0] - nbme_scores[-1] if len(nbme_scores) > 0 else np.nan

        uw_scores = [self.scores["uwsa 1"], self.scores["uwsa 2"]]
        uw_scores = np.sort([v for v in uw_scores if not np.isnan(v)])[::-1]
        self.scores["uwsa max"] = uw_scores[0] if len(uw_scores) > 0 else np.nan
        self.scores["uwsa max2"] = uw_scores[1] if len(uw_scores) > 1 else np.nan

        f120_scores = [self.scores["new free 120"], self.scores["old new free 120"], self.scores["old old free 120"]]
        f120_scores = np.sort([v for v in f120_scores if not np.isnan(v)])[::-1]
        self.scores["free 120 max"] = f120_scores[0] if len(f120_scores) > 0 else np.nan

        max_scores = [self.scores["nbme max"], self.scores["uwsa max"]]
        self.scores["max practice"] = np.nan if all(np.isnan(s) for s in max_scores) else np.nanmax(max_scores)

        self.scores["year"] = self.date.year
        self.scores["month"] = self.date.month

        self.scores["month_cos_2"] = np.cos(self.date.month / 12 * 4 * np.pi)
        
# ------------------------------------------------------------------- #
# --------------------            End            -------------------- #
# ------------------------------------------------------------------- #