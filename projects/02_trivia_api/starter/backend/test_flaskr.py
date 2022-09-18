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
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    """
        In this method we check whether the catgeries route works 
        as desired and returns a dictionary of id and type items
        this test should pass.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    """
        In this method we check whether the questions route works 
        as desired and returns a list of questions. 
        this test should pass.
    """
    def test_get_paginated_questions(self):#should pass
        res = self.client().get('/questions')
        data = json.loads(res.data)
        #categories = Category.query.order_by(Category.id).all()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    """empty message
    """
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    """empty message
    """
    def test_delete_question(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['total_questions']))
        self.assertEqual(question, None)

    """Test 404 Not Found when deleting a question"""
    def test_404_sent_deleting_questions(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 1000).one_or_none()

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

# Not checked for corrections
    # """
    #     In this method the request questions route is beyond 
    #     what is available and returns a list of questions. 
    #     this test should fail as it is beyond our scope.
    # """
    # def test_retrieve_questions_beyond_valid_page(self):#should fail
    #     res = self.client().get('/questions?page=100')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code,400)
    #     self.assertEqual(data['success'],False)
    #     self.assertEqual(data['message'],'resource not found')

    # """
    #     In this method we check whether we can delete a question
    #     given an id.  
    #     this test should pass.
    # """
    # def test_delete_question(self): 
    #     res = self.client().delete('/questions/5')
    #     data = json.loads(res.data)
    #     question = Question.query.filter(Question.id == 5).one_or_none()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(data['deleted'],5)
    #     self.assertEqual(question, None)
    #     self.assertTrue(len(data['questions']))
    #     self.assertTrue(data['total_questions'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()