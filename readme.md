# മോനേ (Mone)
A Malayalam programming language interpreter written in Python.

മോനേ (Mone) is an experimental interpreted programming language that uses Malayalam keywords and syntax to make programming more approachable for Malayalam speakers. The project was developed to explore the design and implementation of programming languages while demonstrating the complete interpreter pipeline—from lexical analysis to execution.

## Features
Malayalam-inspired keywords and syntax
Written entirely in Python
Lexical analyzer (Lexer)
Recursive descent parser
Abstract Syntax Tree (AST) generation
Tree-walk interpreter
Syntax and runtime error reporting
Flask-powered web playground for browser-based execution
Architecture
Source Code
      │
      ▼
   Lexer
      │
      ▼
    Tokens
      │
      ▼
    Parser
      │
      ▼
      AST
      │
      ▼
 Interpreter
      │
      ▼
 Program Output

## Running

Clone the repository:

git clone https://github.com/yourusername/mone.git
cd mone

Install dependencies:

pip install -r requirements.txt

Run the interpreter:

python main.py example.mn

Start the web playground:

python app.py

Then open your browser and navigate to the local Flask server.

## Motivation

Programming languages overwhelmingly use English keywords, which can make the first steps of learning programming less intuitive for native speakers of other languages. Mone explores how a programming language can feel more natural by adopting Malayalam syntax while serving as a learning project for compiler and interpreter construction.

The project focuses on educational value rather than production use, covering the core concepts behind language implementation such as tokenization, parsing, abstract syntax trees, and interpretation.

Technologies
Python
Flask
HTML/CSS/JavaScript (Web Playground)
Future Work
Variables and improved type system
Functions and modules
Lists and dictionaries
Standard library
Better diagnostics and error messages
Performance improvements
Bytecode compiler or virtual machine
References

The implementation was inspired by classic resources on programming language implementation, including:

Crafting Interpreters — Robert Nystrom
Compilers: Principles, Techniques, and Tools (Dragon Book)
Python Documentation
Flask Documentation
License

MIT
