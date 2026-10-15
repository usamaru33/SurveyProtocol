import csv
import re
import os
import difflib
from pathlib import Path

# --- Configuration ---
INPUT_FILE = "screened_included.csv"
CORE_RANKINGS_FILE = "core_rankings.csv"
SJR_RANKINGS_FILE = "sjr_rankings.csv"

OUT_HIGH_RANK = "venue_included_high_rank.csv"
OUT_Q2_REVIEW = "venue_included_q2_review.csv"
OUT_EXCLUDED = "venue_excluded.csv"
OUT_SUMMARY = "venue_screening_summary.txt"

SIMILARITY_THRESHOLD = 0.85

VENUE_ALIASES = ["Venue", "Publication Title", "publication_title", "journal", "booktitle"]
TITLE_ALIASES = ["Title", "title"]
YEAR_ALIASES = ["Year", "Publication Year", "publication_year", "year"]

def generate_dummy_data():
    """Generate dummy ranking data if files do not exist."""
    if not os.path.exists(CORE_RANKINGS_FILE):
        print(f"[*] Generating dummy {CORE_RANKINGS_FILE}...")
        with open(CORE_RANKINGS_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Acronym", "Rank"])
            writer.writerow(["Human Factors in Computing Systems", "CHI", "A*"])
            writer.writerow(["Virtual Reality", "VR", "A"])
            writer.writerow(["User Interface Software and Technology", "UIST", "A*"])
            writer.writerow(["Some Low Rank Conference", "SLRC", "C"])

    if not os.path.exists(SJR_RANKINGS_FILE):
        print(f"[*] Generating dummy {SJR_RANKINGS_FILE}...")
        with open(SJR_RANKINGS_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "SJR Best Quartile"])
            writer.writerow(["IEEE Transactions on Visualization and Computer Graphics", "Q1"])
            writer.writerow(["International Journal of Human-Computer Studies", "Q1"])
            writer.writerow(["Computers & Graphics", "Q2"])
            writer.writerow(["Some Unranked Journal", "-"] )

def normalize_venue(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    # Remove symbols
    name = re.sub(r'[^\w\s]', ' ', name)
    # Stop words removal
    stop_words = [
        r"proceedings\s+of", r"proc\s+of", r"proc", 
        r"conference\s+on", r"journal\s+of", r"transactions\s+on", 
        r"symposium\s+on", r"international", r"the", r"of", r"on", r"in", r"and"
    ]
    for sw in stop_words:
        name = re.sub(r'\b' + sw + r'\b', '', name)
    
    # extra space removal
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def get_best_match(venue_norm: str, ranking_dict: dict, threshold: float = 0.85):
    """
    Tries exact match first, then difflib similarity match.
    Returns (matched_title, rank_info) or (None, None).
    """
    if not venue_norm:
        return None, None
    
    # 1. Exact Match on Normalized Title
    if venue_norm in ranking_dict:
        return ranking_dict[venue_norm]['original_title'], ranking_dict[venue_norm]['rank']
    
    # 2. Similarity Match
    best_match = None
    best_score = 0.0
    for cand_norm, data in ranking_dict.items():
        score = difflib.SequenceMatcher(None, venue_norm, cand_norm).ratio()
        if score > best_score:
            best_score = score
            best_match = cand_norm
            
    if best_score >= threshold and best_match:
        return ranking_dict[best_match]['original_title'], ranking_dict[best_match]['rank']
    
    return None, None

def resolve_col(fieldnames, aliases):
    for a in aliases:
        if a in fieldnames:
            return a
    return None

def main():
    generate_dummy_data()

    # Load Rankings
    core_rankings = {}
    with open(CORE_RANKINGS_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("Title", "")
            rank = row.get("Rank", "")
            if title:
                norm = normalize_venue(title)
                core_rankings[norm] = {'original_title': title, 'rank': rank}
                # Also index by acronym if available
                acronym = row.get("Acronym", "")
                if acronym:
                    core_rankings[acronym.lower()] = {'original_title': title, 'rank': rank}

    sjr_rankings = {}
    with open(SJR_RANKINGS_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("Title", "")
            quartile = row.get("SJR Best Quartile", "")
            if title:
                norm = normalize_venue(title)
                sjr_rankings[norm] = {'original_title': title, 'rank': quartile}

    # Process Input Papers
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file '{INPUT_FILE}' not found. Please prepare the data.")
        # Create a dummy screened_included.csv for test if needed
        print(f"[*] Generating dummy {INPUT_FILE} for testing...")
        with open(INPUT_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Publication Title", "Publication Year"])
            writer.writerow(["Paper A", "Proc. of CHI", "2023"])
            writer.writerow(["Paper B", "IEEE Transactions on Visualization and Computer Graphics", "2022"])
            writer.writerow(["Paper C", "Computers & Graphics", "2021"])
            writer.writerow(["Paper D", "Some Unknown Conference", "2020"])
            writer.writerow(["Paper E", "Virtual Reality", "2023"])
            writer.writerow(["Paper F", "Conference on Human Factors in Computing Systems", "2023"])

    included_high_rank = []
    included_q2 = []
    excluded = []
    
    stats = {
        "total": 0,
        "core_A_star_A": 0,
        "sjr_Q1": 0,
        "sjr_Q2": 0,
        "excluded_unranked": 0,
        "excluded_low_rank": 0
    }

    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        
        venue_col = resolve_col(fieldnames, VENUE_ALIASES)
        if not venue_col:
            print("[ERROR] Could not find a Venue column in the input CSV.")
            return

        # Add tracking columns for output
        out_fields = fieldnames + ["Matched_Venue", "Ranking_Source", "Rank", "Exclusion_Reason"]

        for row in reader:
            stats["total"] += 1
            raw_venue = row.get(venue_col, "")
            norm_venue = normalize_venue(raw_venue)
            
            # Check CORE first (Conferences)
            matched_title, rank = get_best_match(norm_venue, core_rankings, SIMILARITY_THRESHOLD)
            if matched_title:
                row["Matched_Venue"] = matched_title
                row["Ranking_Source"] = "CORE"
                row["Rank"] = rank
                if rank in ["A*", "A"]:
                    stats["core_A_star_A"] += 1
                    row["Exclusion_Reason"] = ""
                    included_high_rank.append(row)
                else:
                    stats["excluded_low_rank"] += 1
                    row["Exclusion_Reason"] = f"CORE Rank {rank} is not A*/A"
                    excluded.append(row)
                continue
            
            # Check SJR if not found in CORE (Journals)
            matched_title, quartile = get_best_match(norm_venue, sjr_rankings, SIMILARITY_THRESHOLD)
            if matched_title:
                row["Matched_Venue"] = matched_title
                row["Ranking_Source"] = "SJR"
                row["Rank"] = quartile
                if quartile == "Q1":
                    stats["sjr_Q1"] += 1
                    row["Exclusion_Reason"] = ""
                    included_high_rank.append(row)
                elif quartile == "Q2":
                    stats["sjr_Q2"] += 1
                    row["Exclusion_Reason"] = "SJR Q2 (Needs Manual Review)"
                    included_q2.append(row)
                else:
                    stats["excluded_low_rank"] += 1
                    row["Exclusion_Reason"] = f"SJR Rank {quartile} is not Q1/Q2"
                    excluded.append(row)
                continue
            
            # Not found in any rankings
            stats["excluded_unranked"] += 1
            row["Matched_Venue"] = "None"
            row["Ranking_Source"] = "None"
            row["Rank"] = "None"
            row["Exclusion_Reason"] = "Venue not found in rankings or matched"
            excluded.append(row)

    # Write output CSVs
    def write_csv(path, rows):
        if not rows: return
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(rows)

    write_csv(OUT_HIGH_RANK, included_high_rank)
    write_csv(OUT_Q2_REVIEW, included_q2)
    write_csv(OUT_EXCLUDED, excluded)

    # Write Summary Text
    with open(OUT_SUMMARY, "w", encoding="utf-8") as f:
        f.write("=== Venue Screening Summary ===\n")
        f.write(f"Total Papers Processed: {stats['total']}\n\n")
        
        f.write("--- INCLUDED ---\n")
        f.write(f"CORE A*/A (High Rank): {stats['core_A_star_A']}\n")
        f.write(f"SJR Q1    (High Rank): {stats['sjr_Q1']}\n")
        f.write(f"Total Included (Auto): {stats['core_A_star_A'] + stats['sjr_Q1']}\n\n")
        
        f.write("--- NEEDS REVIEW (Q2) ---\n")
        f.write(f"SJR Q2 (Manual Check): {stats['sjr_Q2']}\n\n")
        
        f.write("--- EXCLUDED ---\n")
        f.write(f"Low Rank (Not A*/A or Q1/Q2): {stats['excluded_low_rank']}\n")
        f.write(f"Unranked / No Match Found : {stats['excluded_unranked']}\n")
        total_excluded = stats['excluded_low_rank'] + stats['excluded_unranked']
        f.write(f"Total Excluded            : {total_excluded}\n\n")
        
        if stats['total'] > 0:
            match_rate = ((stats['total'] - stats['excluded_unranked']) / stats['total']) * 100
            f.write(f"Venue Match Success Rate: {match_rate:.2f}%\n")

    print(f"[*] Processing complete. Processed {stats['total']} papers.")
    print(f"[*] Included: {stats['core_A_star_A'] + stats['sjr_Q1']}, Q2 Review: {stats['sjr_Q2']}, Excluded: {stats['excluded_low_rank'] + stats['excluded_unranked']}")
    print("[*] See venue_screening_summary.txt for details.")

if __name__ == '__main__':
    main()
