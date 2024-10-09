from flask import Flask, render_template, request

import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.io as pio
import time
import os

app = Flask(__name__)

data = {
    "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
    "Value": [10, 15, 13, 17, 19],
    "Unique Value": [101, 102, 103, 104, 105]  # Unique values for each entry
}

df = pd.DataFrame(data)


def get_entries(add_invalid=False):
    entries = []

    for root, dirs, files in os.walk("data"):
        for file in files:
            with open(os.path.join(root, file), 'r') as file_in:
                temp_dict = json.load(file_in)
                temp_dict['datetime'] = datetime.fromtimestamp(float(temp_dict['ts']))
                if temp_dict['valid']:
                    entries.append(temp_dict)
                elif add_invalid:
                    entries.append(temp_dict)

    return entries


def get_dataframe():
    entries = get_entries()
    df = pd.DataFrame.from_dict(entries)
    return df


# Route for GET request to display the form using form.html from the templates directory
@app.route('/', methods=['GET'])
def entry():
    return render_template('entry.html')


@app.route('/fix', methods=['GET'])
def fix():
    return render_template('fix.html')


def generate_table(df):
    """ Generate an HTML table from a DataFrame. """
    # consider adding CSS for the table
    # arrange the df columns to a way that make more sense
    # transform the date time field

    avoid_columns = ['valid', 'date_override']

    table_html = '<br /><div class="container" id="datatable">'
    # Create table header
    table_html += '<div class="row">'
    for column in df.columns:
        if column in avoid_columns:
            continue
        table_html += f'<div class="col"><b>{column.upper()}</b></div>'
    table_html += '</div>'

    for idx in range(df.shape[0]):
        table_html += '<div class="row">'
        for column in df.columns:
            if column in avoid_columns:
                continue
            table_html += f'<div class="col"><small>{df[column].iloc[idx]}</small></div>'
        table_html += '</div>'

    # Create table body
    table_html += '</div>'

    return table_html


@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Create a Plotly line plot
    df = get_dataframe()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['amount'], mode='lines+markers', name='Values'))

    # Update layout
    fig.update_layout(title='Sample Line Plot', xaxis_title='Date', yaxis_title='Value')

    # Convert the plot to HTML
    plot_html = pio.to_html(fig, full_html=False)

    # Generate the data table procedurally
    table_html = generate_table(df)

    # Render the HTML template with the plot and data table
    return render_template('dashboard.html', plot=plot_html, table=table_html)


# Route for POST request to handle the form submission
@app.route('/submit', methods=['POST'])
def submit():
    whomst = request.form.get('Whomst')
    tag = request.form.get('Tag')
    amount = request.form.get('Amount')
    notes = request.form.get('Notes')
    date_override = request.form.get('Date')
    ts_code = str(time.time())
    with open(f"data/{ts_code}.json", 'w') as file_out:
        json.dump({'whomst': whomst,
                   'tag': tag,
                   'amount': amount,
                   'notes': notes,
                   'date_override': date_override,
                   'ts': ts_code,
                   'valid': True}, file_out)

    return f"Entry ID: {ts_code}"


@app.route('/remove', methods=['POST'])
def remove():
    ts_code = request.form.get('EntryID')
    print(ts_code)
    file_name = f"data/{ts_code}.json"
    if not os.path.exists(file_name):
        return "Entry ID is invalid."

    with open(file_name, 'r') as file_in:
        entry_dict = json.load(file_in)

    entry_dict['valid'] = False

    with open(file_name, 'w') as file_out:
        json.dump(entry_dict, file_out)

    return "Entry has been removed."


if __name__ == '__main__':
    app.run(debug=True)
