from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)
app.config['PORTFOLIO_FOLDER'] = 'static/portfolio'

# Assurez-vous que le dossier portfolio existe et contient vos images
os.makedirs(app.config['PORTFOLIO_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    # Liste toutes les images dans le dossier portfolio
    images = os.listdir(app.config['PORTFOLIO_FOLDER'])
    images = [img for img in images if img.lower().endswith(('png', 'jpg', 'jpeg', 'gif'))]
    return render_template('index.html', images=images)

@app.route('/portfolio/<filename>')
def portfolio_image(filename):
    return send_from_directory(app.config['PORTFOLIO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
