from flask import Blueprint, request, jsonify
from search_module.utils.geocoding_service import geocode_location
from ..utils.insurance_helper import get_provider_ids_by_insurance
from ..utils.specialty_helper import get_taxonomy_code
from mongodb_connection import db

# Create a Blueprint
search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/search', methods=['POST', 'OPTIONS'])
def search():
    data = request.get_json()
    street = data.get("street")
    city = data.get("city")
    state = data.get("state")
    zip_code = data.get("zip")
    specialty = data.get("specialty")
    insurance = data.get("insurance")
    radius_miles = data.get("radius", 10)  # Radius in miles

    # Convert radius from miles to meters
    radius_meters = radius_miles * 1609.34

    # Geocode the location to get latitude and longitude
    lat, lon = geocode_location(street, city, state, zip_code)

    if lat is None or lon is None:
        return jsonify({"error": "Location not found"}), 400

    # Build MongoDB query with geospatial and additional conditions
    query = {
        "geometry": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "$maxDistance": radius_meters
            }
        }
    }

    # Check if given specialty exists
    if specialty:
        taxonomy_code = get_taxonomy_code(specialty)
        if taxonomy_code:
            query["taxonomy_codes"] = {"$in": [taxonomy_code]}
        else:
            return jsonify({"error": "Specialty not found"}), 400

    # Add insurance filter if provided
    if insurance:
        provider_ids = get_provider_ids_by_insurance(insurance)
        if not provider_ids:
            return jsonify({"error": "No providers accept this insurance"}), 404
        query["_id"] = {"$in": provider_ids}

    try:
        results = list(db["provider-data"].find(query, {"_id":0, "type":0, "geometry":0, "provider.Organization Name":0, "provider.Provider First Line Location Address":0, "provider.Provider Second Line Location Address":0, "provider.City":0, "provider.State":0, "provider.Postal Code":0}))
        return jsonify(results), 200
    except Exception as e:
        print("Error querying the database:", e)
        return jsonify({"error": str(e)}), 500