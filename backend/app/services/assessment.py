from app.models.learning import AssessmentAnswerKey, AssessmentResult


def evaluate_answer(
    answer_key: AssessmentAnswerKey,
    learner_answer: str,
    attempts_remaining: int,
) -> AssessmentResult:
    is_correct = learner_answer.strip().casefold() in {
        answer.strip().casefold()
        for answer in answer_key.accepted_answers
    }
    return AssessmentResult(
        assessment_id=answer_key.assessment_id,
        is_correct=is_correct,
        feedback=(
            answer_key.correct_feedback
            if is_correct
            else answer_key.incorrect_feedback
        ),
        explanation=answer_key.explanation,
        attempts_remaining=max(0, attempts_remaining - 1),
    )
