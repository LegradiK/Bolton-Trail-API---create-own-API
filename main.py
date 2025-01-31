from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
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
    altitude: Mapped[int] = mapped_column(Integer, nullable=False)
    route_map: Mapped[str] = mapped_column(String(250))
    trail_distance: Mapped[int] = mapped_column(Integer, nullable=False)
    home_distance: Mapped[int] = mapped_column(Integer, nullable=False)   
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_parking_space: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_cafe: Mapped[bool] = mapped_column(Boolean, nullable=False) 

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

@app.route('/delete/<int:trail_id>')
def delete_trail(trail_id):
    trail_data = db.get_or_404(Trail, trail_id)
    db.session.delete(trail_data)
    db.session.commit()
    return jsonify(response={"success": f"Trail data {trail_id} has been successfully deleted."})

@app.route('/update_data/<int:trail_id>', methods=["POST"])
def update_trail_data(trail_id):
    trail = db.get_or_404(Trail, trail_id)
    new_data = request.get_json()

    if not new_data:
        return jsonify(response={"error": "No data provided"}), 400
    
    for key, value in new_data.items():
        if hasattr(trail, key):
            setattr(trail, key, value)
    
    db.session.commit()
    return jsonify(response={"success": f"trail {trail_id} updated successfully"})


@app.route('/add')
def add_new_trail():
    new_trail = Trail(
        name = request.form.get("name"),
        map_url = request.form.get("map_url"),
        location = request.form.get("location"),
        altitude = request.form.get("altitude"),
        route_map = request.form.get("route_map"),
        trail_distance = request.form.get("trail_distance"),
        home_distance = request.form.get("home_distance"),
        has_toilet = bool(request.form.get("has_toilet")),
        has_parking_space = bool(request.form.get("has_parking_space")),
        has_cafe = bool(request.form.get("has_cafe"))
    )
    db.session.add(new_trail)
    db.session.commit()
    return jsonify(response={"success": "Added a new trail data into the database."})

@app.route('/all', methods=['GET'])
def get_all_trails():
    all_trails = db.session.execute(db.select(Trail)).scalars().all()
    trails = [trail.to_dict() for trail in all_trails]
    return jsonify(trail=trails)

@app.route('/search', methods=['GET'])
def search_trail():
    location = request.args.get('loc')
    if not location:
        return jsonify({"error": "Please provide a location parameter"})
    searching_trails = db.session.execute(db.select(Trail).where(Trail.location == location)).scalars().all()
    if not searching_trails:
        return jsonify({"error": f"No cafes found in {location}"})
    searched_trails = [trail.to_dict() for trail in searching_trails]
    return jsonify(cafe=searched_trails)

@app.route('/random', methods=['GET'])
def get_random_trail():
    all_trails = db.session.execute(db.select(Trail)).scalars().all()
    random_trail = random.choice(all_trails)
    return jsonify(cafe=random_trail.to_dict())

    # return jsonify(cafe={
    #         "id":random_cafe.id,
    #         "name":random_cafe.name,
    #         "map_url":random_cafe.map_url,
    #         "img_url":random_cafe.img_url,
    #         "location":random_cafe.location,
    #         "has_sockets":random_cafe.has_sockets,
    #         "has_sockets":random_cafe.has_sockets,
    #         "has_toilet":random_cafe.has_toilet,
    #         "has_wifi":random_cafe.has_wifi,
    #         "can_take_calls":random_cafe.can_take_calls,
    #         "seats":random_cafe.seats,
    #         "coffee_price":random_cafe.coffee_price
    #     })

    # return jsonify(cafe={
    #     #Omit the id from the response
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
        
    #     #Put some properties in a sub-category
    #     "amenities": {
    #       "seats": random_cafe.seats,
    #       "has_toilet": random_cafe.has_toilet,
    #       "has_wifi": random_cafe.has_wifi,
    #       "has_sockets": random_cafe.has_sockets,
    #       "can_take_calls": random_cafe.can_take_calls,
    #       "coffee_price": random_cafe.coffee_price,
    #     }
    # })



# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
