from flask import Flask, render_template

# Create the Flask application instance
app = Flask(__name__)

# Define the route for the home page
@app.route('/')
def home():
    return "Welcome to the home page!"

# Define the route for the example page
@app.route('/example')
def example():
    return "This is the example page."

# Define a route that accepts a parameter
@app.route('/user/<username>')
def user_profile(username):
    return f"Welcome, {username}!"

# Define a route that renders an HTML template
@app.route('/template')
def render_template_example():
    return render_template('template.html')

# Run the Flask application if this file is the entry point
if __name__ == '__main__':
    app.run()
