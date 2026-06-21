from .models import Question

BASIC_COUNT = 20
SPECIALIST_COUNT = 12

EXAM_STRUCTURE = {
    'basic': {
        3: 10,
        2: 6,
        1: 4,
    },
    'specialist': {
        3: 6,
        2: 4,
        1: 2,
    },
}


def _generate_exam_questions(category_obj):
    """
    Losuje pytania dla danej kategorii zgodnie ze strukturą punktową WORD —
    32 pytania za 74 punkty łącznie.
    """
    all_selected = []

    base_category_qs = Question.objects.filter(category=category_obj)

    basic_qs = base_category_qs.filter(is_basic=True)
    for pts, count in EXAM_STRUCTURE['basic'].items():
        sampled = basic_qs.filter(number_of_points=pts).order_by('?')[:count]
        all_selected.extend(list(sampled))

    specialist_qs = base_category_qs.filter(is_basic=False)
    for pts, count in EXAM_STRUCTURE['specialist'].items():
        sampled = specialist_qs.filter(number_of_points=pts).order_by('?')[:count]
        all_selected.extend(list(sampled))

    return all_selected
