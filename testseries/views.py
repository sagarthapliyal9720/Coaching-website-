from django.shortcuts import render

# Create your views here.
# testseries/views.py
import csv
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, Test, Question

@login_required
def teacher_dashboard(request):
    """Lists all tests created by teachers/admins."""
    tests = Test.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'testseries/teacher_dashboard.html', {'tests': tests, 'categories': categories})


@login_required
def create_category(request):
    """Allows teachers to add exam categories (JEE, NDA, Science, etc.)."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request, "Category already exists!")
        else:
            Category.objects.create(name=name, description=description)
            messages.success(request, f"Category '{name}' created successfully.")
            return redirect('teacher_dashboard')

    return render(request, 'testseries/create_category.html')


@login_required
def create_test(request):
    """Teacher page to set up test metadata."""
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        duration_minutes = request.POST.get('duration_minutes')
        total_marks = request.POST.get('total_marks')
        total_questions = request.POST.get('total_questions')
        
        has_negative = request.POST.get('has_negative_marking') == 'on'
        negative_marks = request.POST.get('negative_marks_per_question', 0)

        category = get_object_or_404(Category, id=category_id)

        test = Test.objects.create(
            title=title,
            category=category,
            duration_minutes=duration_minutes,
            total_marks=total_marks,
            total_questions=total_questions,
            has_negative_marking=has_negative,
            negative_marks_per_question=float(negative_marks) if has_negative else 0.0,
            created_by=request.user
        )

        messages.success(request, f"Test '{test.title}' created! Now add questions.")
        return redirect('manage_questions', test_id=test.id)

    return render(request, 'testseries/create_test.html', {'categories': categories})


@login_required
def manage_questions(request, test_id):
    """Add questions manually or via bulk upload for a test."""
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()

    if request.method == 'POST':
        # Action check: Manual Add or Bulk Upload
        action = request.POST.get('action')

        if action == 'add_manual':
            question_text = request.POST.get('question_text')
            opt_a = request.POST.get('option_a')
            opt_b = request.POST.get('option_b')
            opt_c = request.POST.get('option_c')
            opt_d = request.POST.get('option_d')
            correct = request.POST.get('correct_option')
            marks = request.POST.get('marks', 1)

            Question.objects.create(
                test=test,
                question_text=question_text,
                option_a=opt_a,
                option_b=opt_b,
                option_c=opt_c,
                option_d=opt_d,
                correct_option=correct,
                marks=marks
            )
            messages.success(request, "Question added successfully.")
            return redirect('manage_questions', test_id=test.id)

        elif action == 'bulk_upload':
            file = request.FILES.get('file')
            if not file:
                messages.error(request, "Please select an Excel or CSV file.")
                return redirect('manage_questions', test_id=test.id)

            filename = file.name
            
            # Handle Excel File (.xlsx)
            if filename.endswith('.xlsx'):
                wb = openpyxl.load_workbook(file)
                sheet = wb.active
                # Assuming Row 1 is header: Question, OptA, OptB, OptC, OptD, CorrectOpt, Marks
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if row[0]: # Ensure question_text is not empty
                        Question.objects.create(
                            test=test,
                            question_text=row[0],
                            option_a=row[1],
                            option_b=row[2],
                            option_c=row[3],
                            option_d=row[4],
                            correct_option=str(row[5]).upper().strip(),
                            marks=row[6] if len(row) > 6 and row[6] else 1
                        )
                messages.success(request, "Bulk questions uploaded successfully!")
                return redirect('manage_questions', test_id=test.id)

            # Handle CSV File (.csv)
            elif filename.endswith('.csv'):
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                next(reader, None) # Skip header
                for row in reader:
                    if row and row[0]:
                        Question.objects.create(
                            test=test,
                            question_text=row[0],
                            option_a=row[1],
                            option_b=row[2],
                            option_c=row[3],
                            option_d=row[4],
                            correct_option=row[5].upper().strip(),
                            marks=int(row[6]) if len(row) > 6 and row[6] else 1
                        )
                messages.success(request, "Bulk CSV questions uploaded successfully!")
                return redirect('manage_questions', test_id=test.id)

            else:
                messages.error(request, "Invalid file format! Upload .xlsx or .csv.")

    return render(request, 'testseries/manage_questions.html', {'test': test, 'questions': questions})


# testseries/views.py (Append student views)
import io
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Category, Test, Question, TestResult

@login_required
def student_test_list(request):
    """List all available tests for students."""
    categories = Category.objects.all()
    selected_category = request.GET.get('category')

    if selected_category:
        tests = Test.objects.filter(category__id=selected_category).order_by('-created_at')
    else:
        tests = Test.objects.all().order_by('-created_at')

    return render(request, 'testseries/student_test_list.html', {
        'tests': tests,
        'categories': categories,
        'selected_category': selected_category
    })

# testseries/views.py
import json

@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()

    if request.method == 'POST':
        score = 0.0
        correct_count = 0
        wrong_count = 0
        unattempted_count = 0
        user_answers = {}

        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            user_answers[str(question.id)] = selected_option  # Save choice (e.g. "A", "B", or None)

            if not selected_option:
                unattempted_count += 1
            elif selected_option == question.correct_option:
                correct_count += 1
                score += question.marks
            else:
                wrong_count += 1
                if test.has_negative_marking:
                    score -= test.negative_marks_per_question

        final_score = max(0.0, round(score, 2))

        result = TestResult.objects.create(
            student=request.user,
            test=test,
            score_obtained=final_score,
            total_marks=test.total_marks,
            correct_count=correct_count,
            wrong_count=wrong_count,
            unattempted_count=unattempted_count,
            user_answers=user_answers
        )

        return redirect('test_result', result_id=result.id)

    return render(request, 'testseries/take_test.html', {'test': test, 'questions': questions})


@login_required
def test_result(request, result_id):
    result = get_object_or_404(TestResult, id=result_id, student=request.user)
    questions = result.test.questions.all()

    # Attach user answer directly to each question object for easy template rendering
    detailed_questions = []
    for q in questions:
        user_choice = result.user_answers.get(str(q.id))
        
        # Build option list with status attributes
        options = [
            ('A', q.option_a),
            ('B', q.option_b),
            ('C', q.option_c),
            ('D', q.option_d),
        ]
        
        detailed_questions.append({
            'question': q,
            'user_choice': user_choice,
            'correct_option': q.correct_option,
            'is_correct': user_choice == q.correct_option,
            'is_unattempted': user_choice is None,
            'options': options
        })

    return render(request, 'testseries/test_result.html', {
        'result': result,
        'detailed_questions': detailed_questions
    })


@login_required
def download_result_pdf(request, result_id):
    """Generates and downloads a clean score card PDF."""
    result = get_object_or_404(TestResult, id=result_id, student=request.user)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header Banner
    p.setFillColorRGB(0.0, 0.15, 0.35) # ksBlue
    p.rect(0, 720, 612, 80, fill=1)
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(40, 750, "KS COACHING - TEST RESULT")

    # Student & Test Information
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, 670, f"Student Name: {result.student.full_name}")
    p.drawString(40, 645, f"Test Title: {result.test.title}")
    p.drawString(40, 620, f"Category: {result.test.category.name}")
    p.drawString(40, 595, f"Date: {result.submitted_at.strftime('%Y-%m-%d %H:%M')}")

    p.line(40, 575, 570, 575)

    # Score Metrics
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, 540, f"Score Obtained: {result.score_obtained} / {result.total_marks}")
    
    p.setFont("Helvetica", 12)
    p.drawString(40, 505, f"Correct Answers: {result.correct_count}")
    p.drawString(40, 480, f"Wrong Answers: {result.wrong_count}")
    p.drawString(40, 455, f"Unattempted Questions: {result.unattempted_count}")

    # Footer Notice
    p.setFont("Helvetica-Oblique", 10)
    p.setFillColorRGB(0.4, 0.4, 0.4)
    p.drawString(40, 100, "This is an electronically generated scorecard from KS Coaching Platform.")

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Test_Result_{result.id}.pdf"'
    return response

