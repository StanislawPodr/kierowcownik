from app.questions.models import Question

BASIC_COUNT = 20
SPECIALIST_COUNT = 12

EXAM_STRUCTURE = {
    'basic': {
        3: 10,  # 10 pytań za 3 punkty
        2: 6,   # 6 za 2 pkt
        1: 4,   # 4 za 1 pkt
    },
    'specialist': {
        3: 6,   # 6 pytań za 3 punkty
        2: 4,   # 4 za 2 pkt
        1: 2,   # 2 za 1 pkt
    }
}

def _generate_exam_questions(category_obj):
    """
    Losuje pytania dla danej kategorii zgodnie ze strukturą punktową WORD - 32 pytania za 74 punktów łącznie
    """
    all_selected = []
    
    base_category_qs = Question.objects.filter(category=category_obj)
    
    #Losowanie pytań podstawowych
    basic_qs = base_category_qs.filter(is_basic=True)
    for pts, count in EXAM_STRUCTURE['basic'].items():
        sampled = basic_qs.filter(number_of_points=pts).order_by('?')[:count]
        all_selected.extend(list(sampled))
        
    #Losowanie pytań specjalsitycznych
    specialist_qs = base_category_qs.filter(is_basic=False)
    for pts, count in EXAM_STRUCTURE['specialist'].items():
        sampled = specialist_qs.filter(number_of_points=pts).order_by('?')[:count]
        all_selected.extend(list(sampled))
        
    return all_selected