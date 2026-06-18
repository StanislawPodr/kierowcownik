import json

def generate_exam_cookie_data(session, request):
    session_questions = session.session_questions.all()
    answers_given = session_questions.filter(is_answered=True).count()
    questions_left = session_questions.count() - answers_given
    
    questions_status = {
        str(sq.question.id): "answered" if sq.is_answered else "unanswered"
        for sq in session_questions
    }
    
    return {
        "is_logged_in": request.user.is_authenticated,
        "exam_id": session.id,
        "questions_left": questions_left,
        "answers_given": answers_given,
        "questions_status": questions_status,
        "ends_at": int(session.expires_at.timestamp())
    }