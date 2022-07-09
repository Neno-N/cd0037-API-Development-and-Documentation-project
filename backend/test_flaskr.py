import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'udacity', 'abc', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'id': 101,
            'question': "How many colours are there in the rainbow",
            'answer': 'Seven',
            'category': '1',
            'difficulty': 2
        }

        self.searchTerm = {
            'searchTerm': 'the'
        }

        self.searchTermNone = {
            'searchTerm': ''
        }

        self.playQuiz = {
            "quiz_category": "4",
            "previous_questions": [23]
        }

        self.playQuizNone = {
            "quiz_category": "10",
            "previous_questions": []
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Retrieve questions and paginate

    def test_are_questions_paginated(self):
        result = self.client().get("/questions")
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["current_category"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        result = self.client().get("/questions?page=1000")
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # Retrieve categories
    def test_get_categories(self):
        result = self.client().get("/categories")
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(len(data["categories"]))

    def test_404_wrong_request_in_url(self):
        result = self.client().get("/category")
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # Add a question
    def test_add_new_question(self):
        result = self.client().post("/questions", json=self.new_question)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_405_if_cannot_add_new_question(self):
        res = self.client().post("/questions/45", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method not Allowed")

    # Delete question -> Change id each time
    def test_delete_book(self):
        result = self.client().delete("/questions/16")
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 16)

    def test_422_if_book_does_not_exist(self):
        result = self.client().delete("/questions/1000")
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    # Search Term
    def test_get_question_with_search_term(self):
        result = self.client().post('/search', json=self.searchTerm)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_404_sent_no_search_term(self):
        result = self.client().post('/search', json=self.searchTermNone)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # Get questions from a specific category
    def test_questions_from_specific_category(self):
        result = self.client().get("/categories/3/questions")
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["current_category"]))

    def test_404_no_such_category(self):
        result = self.client().get("/categories/10/questions")
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # Quizzes endpoint
    def test_get_question_from_category_for_quizz(self):
        result = self.client().post('/quizzes', json=self.playQuiz)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(data['previous_questions'])
        self.assertTrue(data['quiz_category'])
        self.assertTrue(data['question'])

    def test_404_no_questions_for_category(self):
        result = self.client().post('/quizzes', json=self.playQuizNone)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
