from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
import sqlite3


class Queries(Resource):
    TABLE_NAME = 'cardqueries'

    parser = reqparse.RequestParser()
    parser.add_argument('query',
        type=str,
        required=True,
        help="This field cannot be left blank!"
    )

    @jwt_required()
    def get(self, name):
        query = self.find_by_name(name)
        if query:
            return query
        return {'message': 'query not found'}, 404

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM {table} WHERE name=?".format(table=cls.TABLE_NAME)
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()

        if row:
            return {'query': {'name': row[0], 'query': row[1]}}

    def post(self, name):
        if self.find_by_name(name):
            return {'message': "An query with name '{}' already exists.".format(name)}

        data = Queries.parser.parse_args()

        qry = {'name': name, 'query': data['query']}

        try:
            Queries.insert(qry)
        except:
            return {"message": "An error occurred inserting the query."}

        return qry

    @classmethod
    def insert(cls, qry):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO {table} VALUES(?, ?)".format(table=cls.TABLE_NAME)
        cursor.execute(query, (qry['name'], qry['query']))

        connection.commit()
        connection.close()

    @jwt_required()
    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM {table} WHERE name=?".format(table=self.TABLE_NAME)
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()

        return {'message': 'query deleted'}

    @jwt_required()
    def put(self, name):
        data = Queries.parser.parse_args()
        qry = self.find_by_name(name)
        updated_query = {'name': name, 'query': data['query']}
        if qry is None:
            try:
                Queries.insert(updated_query)
            except:
                return {"message": "An error occurred inserting the query."}
        else:
             try:
                Queries.update(updated_query)
             except:
                 raise
                 return {"message": "An error occurred updating the query."}
        return updated_query

    @classmethod
    def update(cls, qry):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "UPDATE {table} SET query=? WHERE name=?".format(table=cls.TABLE_NAME)
        cursor.execute(query, (qry['query'], qry['name']))

        connection.commit()
        connection.close()


class Querylist(Resource):
    TABLE_NAME = 'cardqueries'

    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM {table}".format(table=self.TABLE_NAME)
        result = cursor.execute(query)
        queries = []
        for row in result:
            queries.append({'name': row[0], 'query': row[1]})
        connection.close()

        return {'queries': queries}
