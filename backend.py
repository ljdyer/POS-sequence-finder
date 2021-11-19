
# backend.py

# Backend functions for POS sequence finder app

from nltk import ngrams
from nltk.corpus import brown
from tabulate import tabulate

POS_LOOKUP = {
    'ADJ' : 'adjective',
    'ADV' : 'adverb',
    'CONJ' : 'conjunction',
    'DET' : 'determiner',
    'X' : 'other, foreign words',
    'NOUN' : 'noun',
    'PROPN' : 'proper noun',
    'NUM' : 'numeral',
    'PRON' : 'pronoun',
    'ADP' : 'adposition (preposition)',
    'AUX' : 'auxiliary verb',
    'INTJ' : 'interjection',
    'VERB' : 'verb',
    'PART' : 'particle',
    'SCONJ' : 'subordinating conjunction',
    'SYM' : 'symbol'
}

ALL_POS = [[tag, desc] for tag, desc in POS_LOOKUP.items()]

    
# ====================
def pos_list(input_: str) -> str:
    """Parse the input string.

    If it is a valid POS tag sequence, return a list of POS tags.

    If it is not valid, return None."""

    # Convert to uppercase
    input_ = input_.upper()
    # Strip any leading or trailing whitespace
    input_ = input_.strip()
    # Split and remove any extra whitespace between non-space characters
    pos = [p for p in input_.split(' ') if p]

    # Check that the user entered at least two elements
    if len(pos) < 2:
        return None
    # Check that each element is a valid POS tag
    else:
        for p in pos:
            if p.upper() not in POS_LOOKUP.keys():
                return None
        else:
            return pos
    
    
# ====================
def get_matches(pos: list) -> list:
    """Get the list of phrases in the Brown corpus that match the given POS
    tag list"""
    
    # Generate trigrams of tagged words
    brown_all_tagged = brown.tagged_words(tagset='universal')
    n = len(pos)
    brown_tagged_ngrams = ngrams(brown_all_tagged, n)

    # Find three-letter phrases that match the POS sequence
    matches = [" ".join([w for w,t in tagged_ngram])
               for tagged_ngram in brown_tagged_ngrams
               if all([tagged_ngram[i][1] == pos[i]
                       for i in range(n)])]
    return matches
    

# ====================
def get_match_info_string(pos: list, matches: list) -> str:
    """Return a string to inform the user about the matches being
    displayed."""
    
    return f"Showing {len(matches):,} phrase(s) from the Brown " + \
           f"corpus that match the POS sequence {' '.join(pos)}:"


# # ====================
# def write_matches_to_file():
#     pass  
#     # # Write results to a .txt file (if there is at least one match)
#     # if matches: write_matches_to_txt_file(matches, ' '.join(pos)) print()


# # ====================
# def write_matches_to_txt_file(lines: list, filename: str):
#     """Write the list of matches to a text file '[file_name].txt'.

#     If a file with that name already exists, overwrite it.

#     Inform the user whether the write was successful or not"""
    
#     # Get full filename with '.txt' extension
#     full_filename = filename + ".txt"
    


