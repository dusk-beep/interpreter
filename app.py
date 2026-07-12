from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import builtins
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
    raw_inputs = data.get('inputs', [])
    if isinstance(raw_inputs, str):
        input_values = raw_inputs.splitlines()
    else:
        input_values = [str(item) for item in raw_inputs]
    
    output_capture = io.StringIO()
    sys.stdout = output_capture
    original_input = builtins.input
    input_iter = iter(input_values)

    def browser_input(prompt=""):
        print(prompt, end="")
        try:
            return next(input_iter)
        except StopIteration:
            raise EOFError("Not enough input values provided for eduku()")
    
    try:
        builtins.input = browser_input
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        ast = Parser(tokens).parse()
        Interpreter(ast).run()
        
        result = output_capture.getvalue()
    except Exception as e:
        result = f"SYSTEM_ERROR >> {str(e)}"
    finally:
        builtins.input = original_input
        sys.stdout = sys.__stdout__ 
        
    return jsonify({"output": result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
