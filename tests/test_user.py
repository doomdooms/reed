import os, sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
basedir = os.path.abspath(os.path.dirname(__file__))
 
from app import app
from db import db
 
TEST_DB = 'test.db'
 
 
class BasicTests(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.init_app(app)
        db.drop_all(app=app)
        db.create_all(app=app)
 
 
    # executed after each test
    def tearDown(self):
        pass
 
    ########################
    #### helper methods ####
    ########################
 
    def register(self, username, password, question, answer, intro):
        return self.app.post(
            '/register',
            data=dict(username=username, password=password, question=question, answer=answer, intro=intro),
            follow_redirects=True
        )
 
    def login(self, email, password):
        return self.app.post(
            '/auth',
            data=dict(username=username, password=password),
            follow_redirects=True
        )
 
    ###############
    #### tests ####
    ###############
 
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_valid_create_user(self):
        response = self.app.post(
                '/register',
                data=dict(username="mark", password="1018", question="who are you?", answer="i'm mark", intro="My name is ."),
                follow_redirects=True
                )
        self.assertEqual(response.status_code, 201)

    def test_overlapping_username_create_user(self):
        response = self.app.post(
                '/register',
                data=dict(username="mark", password="1018", question="who are you?", answer="i'm mark", intro="My name is ."),
                follow_redirects=True
                )
        self.assertEqual(response.status_code, 201)

        response = self.app.post(
                '/register',
                data=dict(username="mark", password="101", question="wh are you?", answer="im mark", intro="My name is "),
                follow_redirects=True
                )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'The username is already taken', response.data)

    def test_incomplete_request_create_user(self):
        # missing intro
        response = self.app.post(
                '/register',
                data=dict(username="mark", password="101", question="who are you?", answer="I'm mark"),
                follow_redirects=True
                )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'This field is required and cannot be left blank.', response.data)
        # missing answer
        response = self.app.post(
                '/register',
                data=dict(username="mark", password="101", question="who are you?", intro="My name is ."),
                follow_redirects=True
                )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'This field is required and cannot be left blank.', response.data)
        # missing question
        response = self.app.post(
                '/register',
                data=dict(username="mark", password="101", answer="I'm mark", intro="My name is"),
                follow_redirects=True
                )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'This field is required and cannot be left blank.', response.data)
        # missing password 
        response = self.app.post(
                '/register',
                data=dict(username="mark", question="who are you?", answer="I'm mark", intro="My name is"),
                follow_redirects=True
                )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'This field is required and cannot be left blank.', response.data)
        # missing username 
        response = self.app.post(
                '/register',
                data=dict(password="101", question="who are you?", answer="I'm mark", intro="My name is"),
                follow_redirects=True
                )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'This field is required and cannot be left blank.', response.data)

if __name__ == "__main__":
    unittest.main()
