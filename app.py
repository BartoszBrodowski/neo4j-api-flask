from flask import Flask, jsonify, request
from neo4j import GraphDatabase

app = Flask(__name__)

# Create a driver to connect to the Neo4j database
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'test1234'))

# Create a post request to put item into database

@app.route('/add', methods=['POST'])
def add_item():
    # Get the item name from the request
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    position = data['position']
    # Create a session to interact with the database
    with driver.session() as session:
        # Write the query to add the item to the database
        query = 'CREATE (e:Employee {first_name: $first_name, last_name: $last_name, position: $position})'
        # Execute the query
        session.run(query, first_name=first_name, last_name=last_name, position=position)
    # Return a message to the user
    return jsonify({'message': 'Item added to database'})

@app.route('/employees', methods=['GET'])
def get_employees():
    # Get the sort parameter from the query string
    filter = request.args.get('filter')
    sort = request.args.get('sort')

    # Use the driver to get the employees from the Neo4j database
    with driver.session() as session:
        if sort == 'first_name':
            if filter == 'first_name':
                result = session.run("MATCH (e:Employee) RETURN e.first_name ORDER BY e.first_name").data()
            if filter == 'last_name':
                result = session.run("MATCH (e:Employee) RETURN e.last_name ORDER BY e.first_name").data()
            if filter == 'position':
                result = session.run("MATCH (e:Employee) RETURN e.position ORDER BY e.first_name").data()
        
        if sort == 'last_name':
            if filter == 'first_name':
                result = session.run("MATCH (e:Employee) RETURN e.first_name ORDER BY e.last_name").data()
            if filter == 'last_name':
                result = session.run("MATCH (e:Employee) RETURN e.last_name ORDER BY e.last_name").data()
            if filter == 'position':
                result = session.run("MATCH (e:Employee) RETURN e.position ORDER BY e.last_name").data()
        if sort == 'position':
            if filter == 'first_name':
                result = session.run("MATCH (e:Employee) RETURN e.first_name ORDER BY e.position").data()
            if filter == 'last_name':
                result = session.run("MATCH (e:Employee) RETURN e.last_name ORDER BY e.position").data()
            if filter == 'position':
                result = session.run("MATCH (e:Employee) RETURN e.position ORDER BY e.position").data()
        
    
    return jsonify(result)

if __name__ == '__main__':
    app.run()