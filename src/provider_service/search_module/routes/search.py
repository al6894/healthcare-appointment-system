from flask import Blueprint, request, jsonify
from search_module.utils.geocoding_service import geocode_location
from ..utils.insurance_helper import get_provider_ids_by_insurance
from ..utils.specialty_helper import get_taxonomy_code
from mongodb_connection import db

# Create a Blueprint
search_bp = Blueprint('search_bp', __name__)
search_provider_bp = Blueprint("search_provider_bp", __name__)

@search_bp.route('/search', methods=['GET','POST', 'OPTIONS'])
def search():
    if request.method == 'POST':
        data = request.get_json()
        street = data.get("street")
        city = data.get("city")
        state = data.get("state")
        zip_code = data.get("zip")
        specialty = data.get("specialty")
        insurance = data.get("insurance")
        radius_miles = data.get("radius", 10)  # Radius in miles
    elif request.method == 'GET':
        street = request.args.get("street")
        city = request.args.get("city")
        state = request.args.get("state")
        zip_code = request.args.get("zip")
        specialty = request.args.get("specialty")
        insurance = request.args.get("insurance")
        radius_miles = float(request.args.get("radius", 10))  # Convert to float for consistency

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
        results = list(db["provider-data"].find(query, {"type":0, "geometry":0, "properties.NPI":0, "properties.Organization Name":0, "properties.Provider First Line Location Address":0, "properties.Provider Second Line Location Address":0, "properties.City":0, "properties.State":0, "properties.Postal Code":0}).limit(20))
        return jsonify(results), 200
    except Exception as e:
        print("Error querying the database:", e)
        return jsonify({"error": str(e)}), 500
    
@search_provider_bp("search-provider", methods = ['GET'])
def search_provider():
    if request.method == 'GET':
        npi = request.args.get("id")
        
    # Validate that the NPI is provided
    if not npi:
        return jsonify({"error": "NPI is required"}), 400
        
    try:
        # 1447253471
        provider = db["provider-data"].find_one({"properties.NPI": npi}, {"properties.Provider First Line Location Address":0, "properties.Provider Second Line Location Address":0, "properties.City":0, "properties.State":0, "properties.Postal Code":0, "type":0, "geometry":0}) 
        
        # If no provider is found, return an error message
        if not provider:
            return jsonify({"error": "No provider found with the given NPI"}), 404
        
        # Return the provider details
        return jsonify(provider), 200
    except Exception as e:
        # Handle any database or query-related errors
        print("Error querying the database:", e)
        return jsonify({"error": "An internal server error occurred"}), 500