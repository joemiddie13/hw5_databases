from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""

    # TODO: Replace the following line with a database call to retrieve *all*
    # plants from the Mongo database's `plants` collection.
    plants_data = mongo.db.plants.find()

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        # TODO: Get the new plant's name, variety, photo, & date planted, and 
        # store them in the object below.
        new_plant = {
            'name': request.form['plant_name'],
            'variety': request.form['variety'],
            'photo_url': request.form['photo'],
            'date_planted': request.form['date_planted']
        }
        # TODO: Make an `insert_one` database call to insert the object into the
        # database's `plants` collection, and get its inserted id. Pass the 
        # inserted id into the redirect call below.

        result = mongo.db.plants.insert_one(new_plant)
        new_plant_id = str(result.inserted_id)

        return redirect(url_for('detail', plant_id=new_plant_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})
    if not plant_to_show:
        return render_template('404.html'), 404
    harvests = mongo.db.harvests.find({'plant_id': ObjectId(plant_id)})

    context = {
        'plant': plant_to_show,
        'harvests': list(harvests)
    }
    return render_template('detail.html', **context)


@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """

    # TODO: Create a new harvest object by passing in the form data from the
    # detail page form.
    new_harvest = {
        'quantity': request.form['harvested_amount'], # e.g. '3 tomatoes'
        'date': request.form['date_harvested'],
        'plant_id': ObjectId(plant_id)
    }

    # TODO: Make an `insert_one` database call to insert the object into the 
    # `harvests` collection of the database.

    mongo.db.harvests.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""

    # Check if the plant exists in the database
    plant_to_edit = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})
    if not plant_to_edit:
        return render_template('404.html'), 404

    if request.method == 'POST':
        updated_data = {
            'name': request.form['plant_name'],
            'variety': request.form['variety'],
            'photo_url': request.form['photo'],
            'date_planted': request.form['date_planted']
        }

        mongo.db.plants.update_one(
            {'_id': ObjectId(plant_id)},
            {'$set': updated_data}
        )
        
        return redirect(url_for('detail', plant_id=plant_id))
    
    else:
        # Display the edit form with the current plant data
        return render_template('edit.html', plant=plant_to_edit)

    
@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    # Check if the plant exists
    plant_to_delete = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})
    if not plant_to_delete:
        return render_template('404.html'), 404

    # Delete the plant with the given id
    mongo.db.plants.delete_one({'_id': ObjectId(plant_id)})

    # Delete all harvests associated with the given plant id
    mongo.db.harvests.delete_many({'plant_id': ObjectId(plant_id)})

    return redirect(url_for('plants_list'))


if __name__ == '__main__':
    app.run(debug=True)