from flask import Flask, render_template, redirect, url_for, request, send_file

import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.io as pio
import time
import os

app = Flask(__name__)

if not os.path.exists("data/"):
    os.makedirs("data/")


def get_entries(add_invalid=False):
    entries = []

    for root, dirs, files in os.walk("data"):
        for file in files:
            if not file.endswith(".json"):
                continue
            with open(os.path.join(root, file), 'r') as file_in:
                temp_dict = json.load(file_in)
                temp_dict['datetime'] = datetime.fromtimestamp(float(temp_dict['ts']))
                if temp_dict['date_override'] != "":
                    temp_dict['datetime'] = datetime.strptime(temp_dict['date_override'], "%m-%d-%Y")
                if temp_dict['valid']:
                    entries.append(temp_dict)
                elif add_invalid:
                    entries.append(temp_dict)

    return entries


def get_dataframe(add_invalid=False, last_90_days_only=True):
    entries = get_entries(add_invalid)
    df = pd.DataFrame.from_dict(entries)
    df = df.sort_values(["datetime"])
    df['amount'] = df['amount'].astype(int)
    if last_90_days_only:
        mask = df['datetime'].apply(lambda x: (datetime.now() - x) < timedelta(days=90))
        df = df[mask]

    return df


@app.route('/dump', methods=['GET'])
def dump():
    file_name = os.path.join("data/", "dump.csv")
    df = get_dataframe(add_invalid=True, last_90_days_only=False)
    df.to_csv(file_name, index=False)
    return send_file(file_name, as_attachment=True)


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
    df = df.sort_values(['datetime'], ascending=False)
    df = df.reindex(columns=["datetime", 'whomst', 'tag', 'amount', "ts", 'notes'])
    df['datetime'] = df['datetime'].apply(lambda x: x.strftime("%m-%d-%Y"))

    avoid_columns = ['valid', 'date_override']

    table_html = '<br /><div class="container" id="datatable">'
    # Create table header
    table_html += '<div class="row">'
    for column in df.columns:
        table_html += f'<div class="col"><b>{column.upper()}</b></div>'
    table_html += '</div>'

    for idx in range(df.shape[0]):
        table_html += '<div class="row">'
        for column in df.columns:
            table_html += f'<div class="col"><small>{df[column].iloc[idx]}</small></div>'
        table_html += '</div>'

    # Create table body
    table_html += '</div>'

    return table_html


def get_cumulative_plot(df):
    fig = go.Figure()
    df['amount'] = df['amount'].cumsum()
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['amount'], mode='lines+markers', name='Values'))
    fig.update_layout(title='Cumulative Summation Over The Last 90 Days', xaxis_title='Date', yaxis_title='Amount',
                      margin=dict(l=10, r=10, t=40, b=10))
    plot_html = pio.to_html(fig, full_html=False)

    return plot_html


def generate_poc_spending_table(df):
    df['whomst'] = df['whomst'].apply(lambda x: x.upper())
    whomst_set = set(df['whomst'].values)
    spending = []
    for whom in whomst_set:
        temp = dict()
        temp['poc'] = whom
        temp['spent'] = df[df['whomst'] == whom]['amount'].sum()
        spending.append(temp)

    table_html = '<br /><div class="container" id="poctable">'
    table_html += '<div class="row">'
    for column in ['Whomst', 'Spent']:
        table_html += f'<div class="col"><b>{column.upper()}</b></div>'
    table_html += '</div>'

    for entry in spending:
        table_html += '<div class="row">'
        table_html += f'<div class="col"><small>{entry["poc"]}</small></div>'
        table_html += f'<div class="col"><small>{entry["spent"]}</small></div>'

        table_html += '</div>'
    table_html += '</div>'

    return table_html


def generate_spending_bar_chart(df):
    df_sum = df.groupby('tag')['amount'].sum().reset_index()

    # Create the Plotly bar chart
    fig = go.Figure()

    # Add a trace for each unique category
    for category in df_sum['tag'].unique():
        category_data = df_sum[df_sum['tag'] == category]
        fig.add_trace(go.Bar(
            x=category_data['tag'],
            y=category_data['amount'],
            name=category
        ))

    # Update layout for titles and other options
    fig.update_layout(
        title='Spending By Tag Over 90 Days',
        xaxis_title='Tag',
        yaxis_title='Amount',
        barmode='group'  # This groups the bars by category on the same axis
    )

    plot_html = pio.to_html(fig, full_html=False)

    return plot_html


@app.route('/dashboard', methods=['GET'])
def dashboard():
    poc_table = generate_poc_spending_table(get_dataframe())
    table_html = generate_table(get_dataframe())
    plot_html = get_cumulative_plot(get_dataframe())
    bar_plot = generate_spending_bar_chart(get_dataframe())
    return render_template('dashboard.html', plot=plot_html, table=table_html, poc_table=poc_table, bar_plot=bar_plot)


# Route for POST request to handle the form submission
@app.route('/submit', methods=['POST'])
def submit():
    whomst = request.form.get('Whomst')
    tag = request.form.get('Tag')
    amount = request.form.get('Amount')
    notes = request.form.get('Notes')
    date_override = request.form.get('Date')
    ts_code = str(time.time())

    try:
        int(amount)
    except:
        return "Invalid Amount Type"

    try:
        if date_override != "":
            datetime.strptime(date_override, "%m-%d-%Y")
    except:
        return "Invalid Date Override"

    with open(f"data/{ts_code}.json", 'w') as file_out:
        json.dump({'whomst': whomst,
                   'tag': tag,
                   'amount': amount,
                   'notes': notes,
                   'date_override': date_override,
                   'ts': ts_code,
                   'valid': True}, file_out)

    return redirect(url_for('dashboard'))


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

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
