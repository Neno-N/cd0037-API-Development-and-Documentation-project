from audioop import cross
from json import JSONDecodeError
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, questions):
    page = request.args.get("page", 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in questions]
    ques = questions[start:end]

    return ques


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    -Done
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    -Done
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'COntent-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    -Done
    """
    @app.route('/categories')
    def get_categories():
        try:
            all_categories = Category.query.order_by(Category.id).all()
            categories = {
                category.id: category.type for category in all_categories}

            return jsonify({
                "categories": categories
            })
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    -Done
    """
    @app.route('/questions', methods=["GET"])
    def get_questions():
        try:
            all_questions = Question.query.order_by(Question.id).all()
            questions = paginate_questions(request, all_questions)

            all_categories = Category.query.order_by(Category.id).all()
            categories = {
                category.id: category.type for category in all_categories}
            category_id = int(questions[0]['category'])

            return jsonify({
                "total_questions": len(all_questions),
                "questions": questions,
                "categories": categories,
                "current_category": categories[category_id]
            })
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    -Done (reload ain't working though)
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            else:
                Question.delete(question)
                return jsonify({
                    "success": True,
                    "deleted": question_id
                })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    -Done
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
        form = request.get_json()

        new_question = form.get('question', None)
        new_answer = form.get('answer', None)
        new_category = form.get('category', None)
        new_difficulty = form.get('difficulty', None)

        try:
            new_question = Question(question=new_question, answer=new_answer,
                                    category=new_category, difficulty=new_difficulty)
            new_question.insert()

            all_questions = Question.query.order_by(Question.id).all()
            questions = paginate_questions(request, all_questions)

            return jsonify({
                "total_questions": len(all_questions),
                "success": True,
                "questions": questions
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    -Done
    """
    @app.route('/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search_term = body.get('searchTerm')

        if search_term is None or search_term == '':
            abort(404)

        else:
            question_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            questions = paginate_questions(request, question_results)

            return jsonify({
                "questions": questions,
                "total_questions": len(questions)
            })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    -Done
    """
    @app.route('/categories/<int:category_id>/questions')
    def category_questions(category_id):
        id = str(category_id)
        all_questions = Question.query.filter(
            Question.category == id).order_by(Question.id).all()
        questions = paginate_questions(request, all_questions)
        categories = Category.query.filter(Category.id == id)
        current_category = {
            category.id: category.type for category in categories}

        if len(questions) == 0:
            abort(404)

        return jsonify({
            "questions": questions,
            "total_questions": len(questions),
            "current_category": current_category[category_id]
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    -Done
    """
    @app.route('/quizzes', methods=["POST"])
    def do_quizz():

        body = request.get_json()

        category_id = body.get('quiz_category')
        id = str(category_id)
        previous_questions = body.get('previous_questions')

        if category_id == 0:
            questions = Question.query.order_by(Question.id).all()
        else:
            questions = Question.query.filter(
                Question.category == id).order_by(Question.id).all()

        questions = [question.format() for question in questions]

        if len(previous_questions) == len(questions):
            return jsonify({
                "previous_questions": previous_questions,
                "quiz_category": category_id,
                "question": None

            })

        for q in questions:
            x = q["id"]
            if x not in previous_questions:
                question = q

        return jsonify({
            "previous_questions": previous_questions,
            "quiz_category": category_id,
            "question": question
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    -Done
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not Allowed"
        }), 405

    return app
