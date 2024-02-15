from flask import Flask, request, jsonify, session, redirect, url_for, escape, render_template

app = Flask(__name__)

@app.route('/')
