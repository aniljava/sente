
from board import Board, BLACK, WHITE, EMPTY
import sgf

def color(text):
    if text.upper() == 'B':
        return BLACK
    else:
        return WHITE