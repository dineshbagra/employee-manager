from flask import Flask, render_template, request, redirect, send_file, flash
import mysql.connector, os, pandas as pd
from config import DB, SECRET_KEY
from io import BytesIO
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    return mysql.connector.connect(
        host=DB['host'],
        port=DB['port'],
        user=DB['user'],
        password=DB['password'],
        database=DB['database']
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        data = (
            request.form['emp_code'],
            request.form['name'],
            request.form['designation'],
            request.form['department'],
            request.form['dob'],
            request.form['doj'],
            request.form['email']
        )
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO employees (emp_code, name, designation, department, dob, doj, email) VALUES (%s,%s,%s,%s,%s,%s,%s)", data)
        conn.commit()
        cur.close()
        conn.close()
        flash("Employee added successfully!")
        return redirect('/form')
    return render_template('form.html')

@app.route('/view')
def view():
    conn = get_db()
    df = pd.read_sql("SELECT * FROM employees", conn)
    conn.close()
    return render_template('view.html', data=df.to_dict(orient='records'))

@app.route('/download/excel')
def download_excel():
    conn = get_db()
    df = pd.read_sql("SELECT * FROM employees", conn)
    conn.close()
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="employees.xlsx")

@app.route('/download/pdf')
def download_pdf():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    output = BytesIO()
    c = canvas.Canvas(output)
    y = 800
    for row in rows:
        c.drawString(30, y, str(row))
        y -= 20
    c.save()
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="employees.pdf")

if __name__ == '__main__':
    app.run(debug=True)
