from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
import io

# Import your interpreter components
from lexer import Lexer
from myparser import Parser
from interpreter import Interpreter

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    
    output_capture = io.StringIO()
    sys.stdout = output_capture
    
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        ast = Parser(tokens).parse()
        Interpreter(ast).run()
        
        result = output_capture.getvalue()
    except Exception as e:
        result = f"SYSTEM_ERROR >> {str(e)}"
    finally:
        sys.stdout = sys.__stdout__ 
        
    return jsonify({"output": result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
