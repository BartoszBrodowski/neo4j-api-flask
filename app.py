from flask import Flask, jsonify, request
from neo4j._async.driver import AsyncGraphDatabase
import re

app = Flask(__name__)

driver = AsyncGraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'test1234'))


@app.route('/employees', methods=['GET'])
async def get_employees():
    filter = request.args.get('filter')
    sort = request.args.get('sort')
    async with driver.session() as session:
        if sort == 'first_name':
            if filter == 'first_name':
                result = await session.run("MATCH (e:Employee) RETURN e.first_name ORDER BY e.first_name")
                data = await result.data()
            if filter == 'last_name':
                result = await session.run("MATCH (e:Employee) RETURN e.last_name ORDER BY e.first_name")
                data = await result.data()
            if filter == 'position':
                result = await session.run("MATCH (e:Employee) RETURN e.position ORDER BY e.first_name")
                data = await result.data()
        
        if sort == 'last_name':
            if filter == 'first_name':
                result = await session.run("MATCH (e:Employee) RETURN e.first_name ORDER BY e.last_name")
                data = await result.data()
            if filter == 'last_name':
                result = await session.run("MATCH (e:Employee) RETURN e.last_name ORDER BY e.last_name")
                data = await result.data()
            if filter == 'position':
                result = await session.run("MATCH (e:Employee) RETURN e.position ORDER BY e.last_name")
                data = await result.data()
        if sort == 'position':
            if filter == 'first_name':
                result = await session.run("MATCH (e:Employee) RETURN e.first_name ORDER BY e.position")
                data = await result.data()
            if filter == 'last_name':
                result = await session.run("MATCH (e:Employee) RETURN e.last_name ORDER BY e.position")
                data = await result.data()
            if filter == 'position':
                result = await session.run("MATCH (e:Employee) RETURN e.position ORDER BY e.position")
                data = await result.data()
        session.close()
    
    return jsonify(data)

@app.route('/employees', methods=['POST'])
async def add_employee():
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    position = data['position']
    department = data['department']
    async with driver.session() as session:
        queryRelation = 'MATCH (e:Employee {first_name: $first_name, last_name: $last_name, position: $position}) MERGE (d:Department {name: $department}) MERGE (e)-[:WORKS_IN]->(d)'
        await session.run(queryRelation, first_name=first_name, last_name=last_name, position=position, department=department)
    session.close()
    return jsonify({'message': 'Employee added to database'})


# Create PUT request to update employee
@app.route('/employees/<id>', methods=['PUT'])
async def update_employee(id):
    data = request.get_json()
    first_name = data.get('first_name', None)
    last_name = data.get('last_name', None)
    position = data.get('position', None)
    department = data.get('department', None)
    async with driver.session() as session:
        query = f"MATCH (n:Employee) WHERE ID(n) = {id} SET n.first_name = '{first_name}', n.last_name = '{last_name}', n.position = '{position}', n.department = '{department}'"
        await session.run(query, first_name=first_name, last_name=last_name, position=position, department=department)
    session.close()
    return jsonify({'message': 'Item updated in database'})

@app.route('/employees/<id>', methods=['DELETE'])
async def delete_employee(id):
    async with driver.session() as session:
        queryRelation = f"MATCH (e:Employee) WHERE ID(e) = {id} DETACH DELETE e"
        await session.run(queryRelation)

    session.close()
    return jsonify({'message': 'Item deleted from database'})

@app.route('/employees/<id>/subordinates', methods=['GET'])
async def get_subordinates(id):
    async with driver.session() as session:
        queryRelation = f"MATCH (e:Employee)-[:MANAGES]->(d:Employee) WHERE ID(e) = {id} RETURN d"
        result = await session.run(queryRelation)
        data = await result.data()
    session.close()
    return jsonify(data)

@app.route("/employees/<id>/info", methods=["GET"])
async def get_department_info(id):
    department_info = []
    async with driver.session() as session:
        query = f"MATCH (e:Employee)-[:WORKS_IN]->(d:Department) WHERE ID(e) = {id} RETURN d"
        result = await session.run(query)
        data = await result.data()
        department_info.append(data[0])

        query = f"MATCH (e:Employee)-[:WORKS_IN]->(d:Department)<-[:MANAGES]-(m:Employee) WHERE ID(e) = {id} RETURN m"
        result = await session.run(query)
        data = await result.data()
        department_info.append(data)

        query = f"MATCH (e:Employee)-[:WORKS_IN]->(d:Department)<-[:WORKS_IN]-(sub:Employee) WHERE ID(e) = {id} RETURN count(sub)+1 as count"
        result = await session.run(query)
        data = await result.data()
        department_info.append(data)

        await session.close()
    return department_info


@app.route("/departments", methods=["GET"])
async def get_all_departments():
    filter = request.args.get("filter")
    sort = request.args.get("sort")
    if filter:
        [filter_key, filter_value] = filter.split("-")

    async with driver.session() as session:
        whereClause = f'WHERE n.{filter_key}="{filter_value}"' if filter else ""
        orderClause = (
            f", {sort} as c ORDER BY c"
            if re.match("^count", sort)
            else f"ORDER BY n.{sort}"
            if sort
            else ""
        )
        query = f"MATCH (e:Employee)-[r:WORKS_IN]->(n:Department) {whereClause} RETURN n {orderClause}"
        result = await session.run(query)
        data = await result.data()
        await session.close()
        return data

@app.route("/departments/<id>/employees", methods=["GET"])
async def get_employees_by_department(id):
    async with driver.session() as session:
        query = f"MATCH (e:Employee)-[:WORKS_IN]->(d:Department) WHERE ID(d) = {id} RETURN e"
        result = await session.run(query)
        data = await result.data()
        await session.close()
        return data

if __name__ == '__main__':
    app.run()


