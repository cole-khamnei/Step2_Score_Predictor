import os
import json

# ------------------------------------------------------------------- #
# --------------------          Constants        -------------------- #
# ------------------------------------------------------------------- #

# CLIENT_ID = "Client ID"
# CLIENT_SECRET = "Client secrete key"
# USER_AGENT = "reddit user agent name"
# REDIRECT_URI = "personal webpage redirect"

# CLIENT_ID ='nfk6J0DWyQsrcXejFTtN3Q'
# CLIENT_SECRET ='t4VMcyADMtLBfSOWNNFn8kZR-9_O1w'
# USER_AGENT ='medical_student_exam_scraper'
# REDIRECT_URI = "https://github.com/cole-khamnei"


# CLIENT_ID = PERSONAL_API_KEYS["CLIENT_ID"]
# CLIENT_SECRET = PERSONAL_API_KEYS["CLIENT_SECRET"]
# USER_AGENT = PERSONAL_API_KEYS["USER_AGENT"]
# REDIRECT_URI = PERSONAL_API_KEYS["REDIRECT_URI"]
# COMMENT_SAVE_DATA = PERSONAL_API_KEYS["COMMENT_SAVE_DATA"]


COMMENT_SAVE_DATA = "data/comment_save_data.pkl"

PROJECT_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(PROJECT_PATH, "data")
PLOT_PATH = os.path.join(PROJECT_PATH, "plots")
COMMENT_SAVE_PATH = os.path.join(DATA_PATH, "comment_save_data.pkl")
PERSONAL_API_KEYS_PATH = os.path.join(PROJECT_PATH, 'PERSONAL_API_KEYS.json')


COMMENT_REPLACEMENTS = [("\n\n", "\n"), ("-", ":"), ("  ", " "), (" :", ":"),
					    ("NBME ", "NBME"), (": ", ":"), (":", ": "), ("*", ""),
					    ("( ", "("), ("%-", "%:"),  ("score -", "score:"), ("score ", "score:"), 
					   ]

SCORE_RANGES = {
    "step 1": (200, 300),
    "uworld %": (35, 100),
    "uworld % (pass 1)": (35, 100),
    "uworld % (pass 2)": (35, 100),
    "nbme9": (200, 300),
    "nbme10": (200, 300),
    "nbme11": (200, 300),
    "nbme12": (200, 300),
    "nbme13": (200, 300),
    "nbme14": (200, 300),
    "uwsa 1": (200, 300),
    "uwsa 2": (200, 300),
    "new free 120": (35, 100),
    "old new free 120": (35, 100),
    "old old free 120": (35, 100),
    "step 2": (200, 300)
}


NBME_SCORE_KEYS = ["nbme9", "nbme10", "nbme11", "nbme12", "nbme13", "nbme14"]

KEY_ID_PAIRS = {
    "nbme9": ("nbme9:", 3),
    "nbme10": ("nbme10:", 3),
    "nbme11": ("nbme11:", 3),
    "nbme12": ("nbme12:", 3),
    "nbme13": ("nbme13:", 3),
    "nbme14": ("nbme14:", 3),
    "step 2": ("step 2 score:", 3),
    "uwsa 1": ("uwsa 1:", 3),
    "uwsa 2": ("uwsa 2:", 3),
    "new free 120": ("new free 120:", 2),
    "old new free 120": ("old new free 120", 2),
    "old old free 120": ("old old free 120", 2),
}

STEP_2_SCORE_REPLACEMENTS = ["actual score:", "real deal:", "step2:", "actual step 2:",
                             "step 2 ck:", "step 2ck score:", "actual step 2:",
                             "final result:", "step 2 ck score:", "actual step score:",
                             "real score:", "actual:", "actual test:", 
                             "actual step2 score:", "real thing:",
                             "actual step2 ck score:", "step 2:", "actual step 2ck:"
                            ]
STEP_2_SCORE_REPLACEMENTS = [(tk, "step 2 score:") for tk in STEP_2_SCORE_REPLACEMENTS]


with open(PERSONAL_API_KEYS_PATH, 'r') as f:
    PERSONAL_API_KEYS = json.load(f)

CLIENT_ID = PERSONAL_API_KEYS["CLIENT_ID"]
CLIENT_SECRET = PERSONAL_API_KEYS["CLIENT_SECRET"]
USER_AGENT = PERSONAL_API_KEYS["USER_AGENT"]
REDIRECT_URI = PERSONAL_API_KEYS["REDIRECT_URI"]
COMMENT_SAVE_DATA = PERSONAL_API_KEYS["COMMENT_SAVE_DATA"]

# ------------------------------------------------------------------- #
# --------------------            End            -------------------- #
# ------------------------------------------------------------------- #