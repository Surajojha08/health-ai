import ast
import os
import re

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from langdetect import detect
from aixplain.factories import AgentFactory, ModelFactory

load_dotenv()

TEAM_API_KEY = os.getenv("TEAM_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if TEAM_API_KEY:
    os.environ["TEAM_API_KEY"] = TEAM_API_KEY


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


doc_model = ModelFactory.get(get_required_env("DOC_MODEL_ID"))
summ_model = ModelFactory.get(get_required_env("SUMM_MODEL_ID"))
news_model = ModelFactory.get(get_required_env("NEWS_MODEL_ID"))
main_agent = AgentFactory.get(get_required_env("AGENT_MODEL_ID"))

app = Flask(__name__)
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
CORS(app, resources={r"/*": {"origins": cors_origins}})

REQUEST_TIMEOUT = (5, 15)


def remove_markdown(text: str) -> str:
    text = re.sub(r"\*\*.*?\*\*", "", text)
    text = re.sub(r"[\*\-] ", "", text)
    text = re.sub(r"[#\*_\[\]()]", "", text)
    return re.sub(r"\n+", "\n", text).strip()


def format_text(text: str) -> str:
    sections = text.split("\n")
    return "\n\n".join(section.strip() for section in sections if section.strip())


def clean_and_format_response(raw_response: str) -> str:
    if "data=" in raw_response:
        raw_response = raw_response.split("data=", 1)[-1].strip()
    raw_response = raw_response.strip("()'")
    try:
        raw_response = ast.literal_eval(f"'''{raw_response}'''")
    except (SyntaxError, ValueError):
        pass

    match = re.search(
        r"https?://\S+\nSource:.*?\nDate: .*?\n\n",
        raw_response,
        re.DOTALL,
    )
    if not match:
        return raw_response.strip()

    articles_part = raw_response[:match.end()].strip()
    summary_part = raw_response[match.end():].strip()
    formatted_articles = re.sub(r"\n{3,}", "\n\n", articles_part)
    formatted_summary = re.sub(r"\n{3,}", "\n\n", summary_part)
    return f"{formatted_articles}\n\n{'-' * 100}\n\n{formatted_summary}"


def require_json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")
    return data


def get_nearest_health_centers(latitude: float, longitude: float):
    if not GOOGLE_MAPS_API_KEY:
        return {"error": "Google Maps API key is not configured"}

    params = {
        "location": f"{latitude},{longitude}",
        "radius": 5000,
        "type": "hospital",
        "keyword": "public health center",
        "key": GOOGLE_MAPS_API_KEY,
    }
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        return {"error": "No health centers found nearby"}

    centers = []
    for place in results[:5]:
        location = place.get("geometry", {}).get("location", {})
        if "lat" not in location or "lng" not in location:
            continue
        centers.append({
            "name": place.get("name", "Unknown health center"),
            "address": place.get("vicinity", "No address available"),
            "latitude": location["lat"],
            "longitude": location["lng"],
        })
    return centers or {"error": "Health center results had no valid coordinates"}


def get_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    if not GOOGLE_MAPS_API_KEY:
        return {"error": "Google Maps API key is not configured"}

    params = {
        "origin": f"{start_lat},{start_lon}",
        "destination": f"{end_lat},{end_lon}",
        "mode": "driving",
        "key": GOOGLE_MAPS_API_KEY,
    }
    response = requests.get(
        "https://maps.googleapis.com/maps/api/directions/json",
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    routes = response.json().get("routes", [])
    if not routes:
        return {"error": "No route found"}
    polyline = routes[0].get("overview_polyline", {}).get("points")
    if not polyline:
        return {"error": "Route found but no route polyline was returned"}
    return {"route_polyline": polyline}


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = require_json_object()
        question = str(data.get("question", "")).strip()
        if not question:
            return jsonify({"error": "No question provided"}), 400

        try:
            output_language = detect(question)
        except Exception:
            output_language = "en"

        agent_result = main_agent.run(f"{question} Response in {output_language}")
        formatted_response = agent_result.get("data", {}).get("output", "")
        if not formatted_response:
            raise RuntimeError("The AI agent returned an empty response")

        agent_answer = format_text(remove_markdown(str(formatted_response)))
        summ_result = summ_model.run({
            "question": question,
            "response": agent_answer,
            "language": output_language,
        })
        summ_data = summ_result.get("data", "") if isinstance(summ_result, dict) else summ_result
        corrected_text = str(summ_data)
        try:
            corrected_text = corrected_text.encode("latin1").decode("utf-8")
        except UnicodeError:
            pass

        return jsonify({
            "response": agent_answer,
            "summary": format_text(remove_markdown(corrected_text)),
        })
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Error in /ask")
        return jsonify({"error": "Unable to process the request"}), 500


@app.route("/doctors", methods=["POST"])
def find_doctors():
    try:
        data = require_json_object()
        condition = str(data.get("condition", "")).strip()
        location = str(data.get("location", "")).strip()
        if not condition or not location:
            return jsonify({"error": "Condition and location required"}), 400

        result = doc_model.run({"condition": condition, "location": location})
        doctors = str(getattr(result, "data", result))
        try:
            doctors = doctors.encode("latin1").decode("utf-8")
        except UnicodeError:
            pass
        return jsonify({"doctors": doctors})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Error in /doctors")
        return jsonify({"error": "Unable to find doctors"}), 500


@app.route("/health-centers", methods=["POST"])
def find_health_centers():
    try:
        data = require_json_object()
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        if latitude is None or longitude is None:
            return jsonify({"error": "Latitude and longitude are required"}), 400

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            return jsonify({"error": "Latitude and longitude must be numbers"}), 400

        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({"error": "Invalid latitude or longitude"}), 400

        health_centers = get_nearest_health_centers(latitude, longitude)
        if isinstance(health_centers, dict) and "error" in health_centers:
            return jsonify(health_centers), 502

        first_center = health_centers[0]
        route = get_route(
            latitude,
            longitude,
            first_center["latitude"],
            first_center["longitude"],
        )
        return jsonify({"nearest_health_centers": health_centers, "route": route})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except requests.RequestException:
        app.logger.exception("Google Maps request failed")
        return jsonify({"error": "Unable to reach Google Maps"}), 502
    except Exception:
        app.logger.exception("Error in /health-centers")
        return jsonify({"error": "Unable to find nearby health centers"}), 500


@app.route("/news", methods=["POST"])
def get_news():
    try:
        data = require_json_object()
        language = str(data.get("language", "")).strip()
        if not language:
            return jsonify({"error": "Language selection is required"}), 400
        news = news_model.run({"language": language})
        return jsonify({"news": clean_and_format_response(str(news))})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Error in /news")
        return jsonify({"error": "Unable to fetch news"}), 500


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify({"error": "HTTP method not allowed"}), 405


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
