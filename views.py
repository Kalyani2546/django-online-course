from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, Enrollment, Question, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = get_object_or_404(Enrollment, user=user, course=course)
    
    if request.method == 'POST':
        selected_ids = []
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                selected_ids.append(int(value))
        
        submission = Submission.objects.create(enrollment=enrollment)
        submission.choices.set(selected_ids)
        submission.save()
        
        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_choices = submission.choices.all()
    selected_ids = [c.id for c in selected_choices]
    
    total_score = 0
    total_grade = 0
    
    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            total_grade += question.grade
            if question.is_get_score(selected_ids):
                total_score += question.grade
                
    percentage = int((total_score / total_grade) * 100) if total_grade > 0 else 0
    
    context['course'] = course
    context['selected_ids'] = selected_ids
    context['total_score'] = total_score
    context['total_grade'] = total_grade
    context['percentage'] = percentage
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
