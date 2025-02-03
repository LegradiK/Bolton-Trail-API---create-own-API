from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Float
import random

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trails.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE ConfigurationS
class Trail(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    altitude: Mapped[int] = mapped_column(Integer)
    route_map: Mapped[str] = mapped_column(String(250))
    trail_distance: Mapped[int] = mapped_column(Float, nullable=False)
    home_distance: Mapped[int] = mapped_column(Float)   
    has_toilet: Mapped[bool] = mapped_column(Boolean)
    has_parking_space: Mapped[bool] = mapped_column(Boolean)
    has_cafe: Mapped[bool] = mapped_column(Boolean) 

    def to_dict(self):
        dictionary = {}
         # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        
        # #Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/delete/<int:trail_id>', methods=["DELETE"])
def delete_trail(trail_id):
    trail_data = db.get_or_404(Trail, trail_id)

    if not trail_data:
        return jsonify(response={"error":f"Trail with the trial_id {trail_id} not found."})

    db.session.delete(trail_data)
    db.session.commit()

    db.session.remove()

    return jsonify(response={"success": f"Trail data {trail_id} has been successfully deleted."})

@app.route('/update_data/<int:trail_id>', methods=["POST"])
def update_trail_data(trail_id):
    trail = db.get_or_404(Trail, trail_id)

    updated_fields = {}

    name = request.form.get('name')
    map_url = request.form.get('map_url')
    location = request.form.get('location')
    altitude = request.form.get('altitude')
    route_map = request.form.get('route_map')
    trail_distance = request.form.get('trail_distance')
    home_distance = request.form.get('home_distance')
    # Correctly handle boolean fields
    has_toilet = request.form.get('has_toilet')
    has_parking_space = request.form.get('has_parking_space')
    has_cafe = request.form.get('has_cafe')

    # Update the trail object only if the form field is provided
    if name:
        trail.name = name
        updated_fields["name"] = name
    if map_url:
        trail.map_url = map_url
        updated_fields["map_url"] = map_url
    if location:
        trail.location = location
        updated_fields["location"] = location
    if altitude:
        trail.altitude = altitude
        updated_fields["altitude"] = altitude
    if route_map:
        trail.route_map = route_map
        updated_fields["route_map"] = route_map
    if trail_distance:
        trail.trail_distance = trail_distance
        updated_fields["trail_distance"] = trail_distance
    if home_distance:
        trail.home_distance = home_distance
        updated_fields["home_distance"] = home_distance
    if has_toilet is not None:
        trail.has_toilet = has_toilet == "true"
        updated_fields["has_toilet"] =has_toilet
    if has_parking_space is not None:
        trail.has_parking_space = has_parking_space == "true"
        updated_fields["has_parking_space"] = has_parking_space
    if has_cafe is not None:
        trail.has_cafe = has_cafe == "true"
        updated_fields["has_cafe"] = has_cafe

    if updated_fields:
        db.session.commit()
        db.session.remove()
        # print(updated_fields)
        return jsonify(response={
            "success": f"Updated a trail data in the database.",
            "trail_id": f"{trail_id}",
            "updated_fields":updated_fields
        })

    else:
        return jsonify({"error": "No fields were updated"})



@app.route('/add', methods=["POST"])
def add_new_trail():
    # Insert into database
    new_trail = Trail(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        location=request.form.get("location"),
        altitude=request.form.get("altitude"),
        route_map=request.form.get("route_map"),
        trail_distance=request.form.get("trail_distance"),
        home_distance=request.form.get("home_distance"),
        has_toilet=bool(request.form.get("has_toilet")),
        has_parking_space=bool(request.form.get("has_parking_space")),
        has_cafe=bool(request.form.get("has_cafe"))
    )
    print(new_trail)
    db.session.add(new_trail)
    db.session.commit()

    db.session.remove()

    return jsonify(response={"success": "Added a new trail data into the database."})


@app.route('/all', methods=['GET'])
def get_all_trails():
    all_trails = db.session.execute(db.select(Trail)).scalars().all()
    trails = [trail.to_dict() for trail in all_trails]
    return jsonify(trail=trails)

@app.route('/search_by_location', methods=['GET'])
def search_trail_by_location():
    location = request.args.get('loc')
    if not location:
        return jsonify({"error": "Please provide a location parameter"})
    searching_trails = db.session.execute(db.select(Trail).where(Trail.location == location)).scalars().all()
    if not searching_trails:
        return jsonify({"error": f"No trails found in {location}"})
    searched_trails = [trail.to_dict() for trail in searching_trails]
    return jsonify(trail=searched_trails)

@app.route('/search_by_distance', methods=['GET'])
def search_trail_by_distance():
    distance = int(request.args.get('distance'))
    if not distance:
        return jsonify({"error": "Please provide a distance parameter"})
    try:
        distance = int(distance)
    except ValueError:
        return jsonify({"error": "Invalid distance value. Please enter a number."}), 400

    if distance <= 5:
        distance_range = (0, 5)
    elif distance <= 10:
        distance_range = (6, 10)
    elif distance <= 20:
        distance_range = (11, 20)
    elif distance <=30:
        distance_range = (21, 30)
    else:
        distance_range = (31, 100)
    
    searching_trails = db.session.execute(db.select(Trail).where(Trail.trail_distance.between(*distance_range))).scalars().all()
    if not searching_trails:
        return jsonify({"error": f"No trails found within the range of {distance_range[0]} - {distance_range[1]} km distance"}), 404
    searched_trails = [trail.to_dict() for trail in searching_trails]
    return jsonify(trail=searched_trails)

@app.route('/random', methods=['GET'])
def get_random_trail():
    all_trails = db.session.execute(db.select(Trail)).scalars().all()
    random_trail = random.choice(all_trails)
    return jsonify(trail=random_trail.to_dict())


if __name__ == '__main__':
    app.run(debug=True)
