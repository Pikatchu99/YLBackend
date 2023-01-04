
import unittest
import requests
import json
import flask
from app import APP
from ast import literal_eval
from flask import Flask, jsonify

class FlaskTest(unittest.TestCase):    
    def setUp(self):
        self.app = APP.test_client()

    def test_successful_login1(self):
        payload = json.dumps({
            "phone_email": "96560024",
            "password": "000000"
        })
        response = self.app.post('/auth/login', headers={"Content-Type": "application/json"}, data=payload)
        self.assertEqual(201, response.status_code)
        
    def test_bad_login1(self):
        payload = json.dumps({
            "phone_email": "96560024",
            "password": "0000fcycfv00"
        })
        response = self.app.post('/auth/login', headers={"Content-Type": "application/json"}, data=payload)

    def test_successful_register(self):
        payload = json.dumps({
              "phone": "33333333",
              "firstname": "Plu3",
              "surname": "DIM3",
              "role": "proprietaire",
              "country": "Bénin",
              "town": "Cotonou",
              "district": "Agla",
              "email": "string3@gmail.com",
              "password": "333333"
        })
        response = self.app.post('/auth/register', headers={"Content-Type": "application/json"}, data=payload)
    
    def test_bad_register(self):
        payload = json.dumps({
              "phone": "33333333",
              "firstname": "Plu3",
              "surname": "DIM3",
              "role": "proprietaire",
              "country": "Bénin",
              "town": "Cotonou",
              "district": "Agla",
              "email": "string33@gmail.com",
              "password": "333333"
        })
        response = self.app.post('/auth/register', headers={"Content-Type": "application/json"}, data=payload)
    
    def test_succesful_logout(self):
        payload = json.dumps({
            "token" : "azertyu123456ki98765ytreza"
        })
        response = self.app.post('/auth/logout', headers={"Content-Type": "application/json"}, data=payload)

if __name__ == "__main__":
    unittest.main()
