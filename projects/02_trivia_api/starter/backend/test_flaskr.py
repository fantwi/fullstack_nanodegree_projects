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
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', 'cr122', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'Who was the US president in 2021',
            'answer': 'Joe Biden',
            'category': '4',
            'difficulty': '4',
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    """
        Test getting all categories. This test should pass.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    """
        Test getting paginated questions. This test should pass.
    """
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        #categories = Category.query.order_by(Category.id).all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    """
        Test requesting for an invalid page. This test should fail.
    """
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    """
        Test deleting a question. This test should pass.
    """
    def test_delete_question(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 5)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(question, None)

    """
        Test 422 Unprocessable sent if question does not exist 
        when deleting a question. This test should fail.
    """
    def test_422_sent_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    """
        Test the creation of a new question. This test should pass. 
    """
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['created'])
        self.assertTrue(body['total_questions'])
        self.assertTrue(len(body['questions']))

    """
        Test 405 if question creation is not allowed. This test should fail.
    """
    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post('/question/50', json=self.new_question)
        body = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['message'], 'Method not allowed')

    # """
    #     Test 422 Unprocessable when no question id is 
    #     provided when deleting a question
    # """
    # def test_422_sent_deleting_questions(self):
    #     res = self.client().delete('/questions')
    #     data = json.loads(res.data)

    #     question = Question.query.filter(Question.id == None).one_or_none()

    #     self.assertEqual(res.status_code, 422)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'Unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()