import praw
import time
import numpy as np
from datetime import datetime, timezone
from reddit_api_key import key
from reddit_utils import reddit 


# -----------------------------
# CONFIG
# -----------------------------
MAX_COMMENTS = 1000
MAX_POSTS = 1000


# -----------------------------
# BOT SCORING FUNCTIONS
# -----------------------------
def score_account_age(account_age_days):
    if account_age_days < 7:
        return 30
    elif account_age_days < 30:
        return 15
    elif account_age_days < 365:
        return 5
    return 0


def score_post_frequency(items_per_day):
    if items_per_day > 50:
        return 30
    elif items_per_day > 20:
        return 15
    elif items_per_day > 10:
        return 5
    return 0


def score_duplicate_rate(dup_rate):
    if dup_rate > 0.5:
        return 
    elif dup_rate > 0.3:
        return 15
    elif dup_rate > 0.1:
        return 5
    return 0


def score_short_comment_ratio(r):
    if r > 0.7:
        return 20
    elif r > 0.4:
        return 10
    elif r > 0.2:
        return 5
    return 0


# -----------------------------
# MAIN ANALYSIS FUNCTION
# -----------------------------
def analyze_user(username, reddit):
    user = reddit.redditor(username)

    # Timestamps
    created = datetime.fromtimestamp(user.created_utc, timezone.utc)
    account_age_days = (datetime.now(timezone.utc) - created).days

    # Activity lists
    comments = list(user.comments.new(limit=MAX_COMMENTS))
    posts = list(user.submissions.new(limit=MAX_POSTS))
    all_items = comments + posts

    if len(all_items) == 0:
        return {"error": "User has no visible activity."}

    # Compute posting frequency
    timestamps = [c.created_utc for c in all_items]
    items_per_day = len(timestamps) / ((max(timestamps) - min(timestamps)) / 86400 + 1)

    # Duplicate comment detection
    comment_bodies = [c.body.strip().lower() for c in comments]
    if comment_bodies:
        unique = len(set(comment_bodies))
        dup_rate = 1 - (unique / len(comment_bodies))
    else:
        dup_rate = 0

    # Short (low-effort) comments
    short_comments = [c for c in comments if len(c.body.strip()) < 15]
    short_ratio = len(short_comments) / max(len(comments), 1)

    # Subreddit diversity
    subreddits = [i.subreddit.display_name for i in all_items]
    unique_subs = len(set(subreddits))

    # Karma stats
    total_karma = (user.link_karma + user.comment_karma)


    # Scoring
    else:
        score = (score_account_age(account_age_days)
            + score_post_frequency(items_per_day)
            + score_duplicate_rate(dup_rate)
            + score_short_comment_ratio(short_ratio)
        )

    bot_likelihood = min(100, score)



    return {
        "username": username,
        "bot_likelihood": bot_likelihood,
        "account_age_days": account_age_days,
        "items_per_day": items_per_day,
        "duplicate_comment_rate": dup_rate,
        "short_comment_ratio": short_ratio,
        "unique_subreddits": unique_subs,
        "total_karma": total_karma,
        "sample_comments": comment_bodies[:10],
    }


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":


    username = input("Enter Reddit username to analyze: ").strip()
    result = analyze_user(username, reddit)

    if "error" in result:
        print("Error:", result["error"])
    else:
        print("\n=== BOT ANALYSIS REPORT ===")
        for k, v in result.items():
            print(f"{k}: {v}")
