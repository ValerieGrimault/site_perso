from flask import Flask, url_for, render_template, request, make_response
import requests
import json
from sklearn.externals import joblib
import re #module d'expressions régulières
app = Flask(__name__)

dark_sky_api_key="58661b65ef4f40d860faa0fa9bebc256"
ipstack_api_key ="ea7719f262176b477a985688f18f4c51"

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", name="Valérie Grimault")
    elif request.method == "POST":
        response = make_response(render_template("project.html"))
        return response

@app.route("/project", methods=["GET", "POST"])
def project():
    current_location = requests.get("http://api.ipstack.com/check", params={"access_key" : ipstack_api_key})
    current_location = current_location.json()
    latitude = current_location["latitude"]
    longitude = current_location["longitude"]
    ville = current_location["city"]
    weather = requests.get("https://api.darksky.net/forecast/{}/{},{}".format(dark_sky_api_key, latitude, longitude))
    weather = weather.json()
    if request.method == "GET":
        return render_template("project.html", weather = weather, ville = ville)
    elif request.method == "POST":
        nom = request.form["nom_utilisateur"]
        email = request.form["email_utilisateur"]
        message = request.form["message_utilisateur"]
        response = make_response(render_template("project.html", ville = ville, weather = weather , name = nom, email = email, message = message))
        response.set_cookie("Nom", nom)
        return response

@app.route("/urls")
def urls():
    nom = request.cookies.get("Nom")
    return render_template("url.html", nom = nom)


@app.route("/predict", methods=["GET", "POST"])
def predict():
	
	xp_str = [[request.form["regression"]]]
	
	# si la donnée (sans les espaces non significatives) n'est pas vide
	if xp_str[0][0].strip() != '':
		# on vérifie si la saisie correspond à un nombre. Si c'est un nombre, on fait la prédiction du salaire
		regexp = r"(^[0-9]+)((\.)([0-9]+))?"
		if re.match(regexp, xp_str[0][0]) is not None:
			regressor = joblib.load("./linear_regression_model.pkl")
			xp = [[float(request.form["regression"])]]
			print("pas vide")
			print("appel algo")
			y_pred = float(regressor.predict(xp))
			return render_template("predicted.html", xp = xp[0][0], y_pred = y_pred)
		# si ce n'est pas un nombre, on ne peut pas prédire le salaire
		else:
			print("nombre d'année d'expérience invalide")
			return render_template("predicted.html")
	# sinon, si l'utilisateur n'a rien renseigné, on ne peut pas prédire le salaire
	else:
		print("vide")
		return render_template("predicted.html")

		


if __name__ == "__main__":
    app.run(debug=True)
