import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category  

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Contorl-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    
    return response
  
  '''helper method to paginate questions'''
  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    question = [question.format() for question in selection]
    current_questions = question[start:end]
  
  
  '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    formatted_categories = [category.format for category in categories]

    if len(formatted_categories) == 0:
      abort(404)

    return jsonify({
      'Success': True,
      'Categories': formatted_categories,
      'Total Categories': len(formatted_categories)
    })

  '''
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    '''to get by page number'''
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.all()
    formatted_questions = [question.format() for question in questions]
    categories = Category.query.all()
    formatted_categories = [Category.format() for category in categories]

    return jsonify({
      'Questions': formatted_questions[start:end],
      'Total Questions':len(formatted_questions),
      'Current Category': None,
      'Categories': formatted_categories
    })
  '''
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id', methods = ['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if book is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'Success': True,
        'Deleted': question_id,
        'Questions': current_questions,
        'Total_questions': len(Question.query.all())
      })

    except:
      abort(422)

  '''
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)

    try:
      if search:
        selection = Question.query.order_by(Question.id).filter(Question.title.ilike('%{}%'.format(search)))
        current_questions = paginate_questions(request, selection)

        return jsonify({
          'Success': True,
          'Questions': current_questions,
          'Total_questions': len(Question.query.all())
        })

      else:
        question = Question(question= new_question, answer = new_answer, difficulty = new_difficulty, category = new_category)
        question.insert()

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
          'Success': True,
          'Created': question.id,
          'Questions': current_questions,
          'Total Questions': len(Question.query.all())
        })

    except:
      abort(422)

  '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/<int:question.id', methods= ['POST'])
  def search_for_questions():
    body = request.get_json()
    search_by = body.get('search by', None)

    if search_by:
      results = Question.query.filter(Question.question.ilike('%{}%'.format(search_by))).all()

      return jsonify({
        'Success': True,
        'Questions': [question.format() for question in results],
        'Total_questions': len(results),
        'Current_category': None
      })
        
    abort(404)

  ''' 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_question_by_category(category_id):

    try:
      questions = Question.query.filter(Question.category == str(category_id)).all()

      return jsonify({
        'Success': True,
        'Questions': [question.format() for question in questions],
        'Total_questions': len(questions),
        'Current_category': category_id
      })
      
    except:
      abort(404)

  '''
  
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def play_trivia():
    try:
      body = request.get_json()

      if not('quiz_category' in body or 'previous_questions' in body):
        abort(422)

      category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')

      if category['type'] == 'click':
        possible_questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
      
      else:
        possible_questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_((previous_questions))).all()

      next_question = possible_questions[random.randrange(0, len(possible_questions))].format() if len(possible_questions) > 0 else None

      return jsonify({
        'Success': True,
        'Question': next_question
      })
        
    except:
      abort(422)

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not found'
    }),404 

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    }),422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request'
    }),400

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method not allowed'
    }),405

  return app

    