"""Secret santa draw generator logic."""

import random

from secret_santa.config import settings


class NoSolutionError(Exception):
    pass


def generate_draw(participants: list[int], blacklists: dict[int, list[int]]) -> dict | None:
    """
    Simple draw generator function.

    We'll try to provide a random solution with given blacklist constraints. If no
    solution can be found after MAX_DRAW_GENERATION_ATTEMPTS, we give up.

    FIXME: this can be improved after POC validation
    """
    if len(participants) <= 1:
        return None

    for iterator in range(settings.MAX_DRAW_GENERATION_ATTEMPTS):
        remaining = participants[:]
        result = {}
        random.shuffle(remaining)
        try:
            for participant in participants:
                possibilities = [
                    option for option in remaining
                    if option != participant and option not in blacklists.get(participant, [])
                ]
                if not possibilities:
                    raise NoSolutionError
                choice = random.choice(possibilities)
                result[participant] = choice
                remaining.remove(choice)
            return result
        except NoSolutionError:
            continue

    return None
