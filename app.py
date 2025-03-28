import matplotlib
matplotlib.use('Agg')  # Iestata, lai matplotlib izmantotu bez GUI režīmu

from flask import Flask, render_template
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from peewee import *

# Flask aplikācijas inicializēšana
app = Flask(__name__)

# Datubāzes savienojuma izveide (izmanto to, ko mēs iepriekš izveidojām)
db = SqliteDatabase('albums.db')

# Izveido tabulu (ja vēl nav)
class Album(Model):
    artist = CharField()
    album = CharField()
    plays = IntegerField()

    class Meta:
        database = db

# Aizpildām datubāzi ar datiem (piemērs)
@app.before_request
def create_tables():
    db.connect()
    db.create_tables([Album], safe=True)

    # Pārbaudu, vai tabulā ir dati
    if Album.select().count() == 0:
        Album.create(artist="Mākslinieks 1", album="Albums 1", plays=100)
        Album.create(artist="Mākslinieks 2", album="Albums 2", plays=150)
        Album.create(artist="Mākslinieks 3", album="Albums 3", plays=200)

# Maršruts sākumlapai
@app.route('/')
def index():
    albums = Album.select()

    # Pārbaudu, vai datu bāzē ir dati
    if albums.count() == 0:
        return "Datubāzē nav datu."

    # Iegūstu visus māksliniekus un to kopējo atskaņojumu skaitu
    artist_data = {}
    for album in albums:
        if album.artist not in artist_data:
            artist_data[album.artist] = 0
        artist_data[album.artist] += album.plays

    # Iegūstu mākslinieku nosaukumus un to kopējo atskaņojumu skaitu
    artist_names = list(artist_data.keys())
    total_plays = list(artist_data.values())

    # Stabiņu diagramma
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(artist_names, total_plays, color='skyblue')
    ax1.set_xlabel('Mākslinieks')
    ax1.set_ylabel('Atskaņojumu skaits')
    ax1.set_title('Atskaņojumu skaits katram māksliniekam')
    plt.xticks(rotation=90)

    # Saglabāju attēlu stabiņu diagrammai
    img1 = BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    img_base64_1 = base64.b64encode(img1.getvalue()).decode('utf8')
    plt.close(fig1)  # Atbrīvo atmiņu

    # Histogramma
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.hist(total_plays, bins=10, color='orange', edgecolor='black')
    ax2.set_xlabel('Atskaņojumu skaits')
    ax2.set_ylabel('Mākslinieku skaits')
    ax2.set_title('Atskaņojumu skaita sadalījums')

    # Saglabāju attēlu histogrammai
    img2 = BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    img_base64_2 = base64.b64encode(img2.getvalue()).decode('utf8')
    plt.close(fig2)  # Atbrīvo atmiņu

    # Atgriež HTML lapu ar abiem attēliem
    return render_template('index.html', img_base64_1=img_base64_1, img_base64_2=img_base64_2)

if __name__ == '__main__':
    app.run(debug=True)
  
