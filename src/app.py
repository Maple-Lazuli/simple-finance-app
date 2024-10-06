from flask import Flask, render_template, request

app = Flask(__name__)


# Route for GET request to display the form
@app.route('/', methods=['GET'])
def index():
    return '''
    <html>
        <body>
            <h2>Input Form</h2>
            <form action="/submit" method="POST">
                <label for="name">Enter your name:</label><br>
                <input type="text" id="name" name="name"><br><br>
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    '''


# Route for POST request to handle the form submission
@app.route('/submit', methods=['POST'])
def submit():
    user_name = request.form.get('name')
    if user_name:
        return f'<h3>Hello, {user_name}!</h3>'
    else:
        return '<h3>Please provide a name.</h3>'


if __name__ == '__main__':
    app.run(debug=True)
