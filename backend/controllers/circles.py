from flask import Blueprint, jsonify, request
from ..db import connect_db
from flask_jwt_extended import jwt_required, get_jwt
from ..validators.circles_validators import add_circle_middleware, update_circle_middleware

circles_bp = Blueprint('circles', __name__, url_prefix='/circles')

# Main circles endpoints
@circles_bp.route('/all')
@jwt_required()
def get_all_circles():
    try:
        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT circles.*, users.username FROM circles
	                    JOIN users ON circles.host_id = users.id
	                    ORDER BY start_date
                        """)
            data = cur.fetchall()
        
        return jsonify({ 'status': 'ok', 'msg': 'successfully fetched all circles', 'data': data }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'error getting all circles'}), 400

@circles_bp.route('/get', methods=['POST'])
@jwt_required()
def get_circle_by_id():
    try:
        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            circle_id = request.json.get('circle_id')
            cur.execute("""
                        SELECT circles.*, users.username FROM circles
	                    JOIN users ON circles.host_id = users.id
                        WHERE circles.id = %s
                        """, (circle_id,))
            data = cur.fetchone()

            if not data:
                return jsonify({ 'status': 'error', 'msg': 'circle does not exist'})
        
        return jsonify({ 'status': 'ok', 'msg': 'successfully fetched circle details', 'data': data }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'error getting circle details'}), 400

@circles_bp.route('/following', methods=['GET'])
@jwt_required()
def get_following_circles():
    try:
        claims = get_jwt()
        logged_in_user_id = claims['id']

        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT circles.*, users.username FROM circles
	                    JOIN users ON circles.host_id = users.id
                        JOIN follow_relationships ON follow_relationships.user_id = users.id
                        WHERE follow_relationships.follower_id = %s
                        ORDER BY circles.start_date
                        """, (logged_in_user_id,))
            data = cur.fetchall()
        return jsonify({ 'status': 'ok', 'msg': 'successfully fetched following circles', 'data': data }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'error getting following circles'}), 400

@circles_bp.route('/user', methods=['POST'])
@jwt_required()
def get_circles_by_user():
    try:
        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            host_id = request.json.get('host_id')
            cur.execute("""
                        SELECT circles.*, users.username FROM circles
	                    JOIN users ON circles.host_id = users.id
                        WHERE circles.host_id = %s
                        ORDER BY circles.start_date
                        """, (host_id,))
            data = cur.fetchall()

            if not data:
                return jsonify({ 'status': 'ok', 'msg': 'user has no circles'}), 200
        
        return jsonify({ 'status': 'ok', 'msg': 'successfully fetched all circles by user', 'data': data }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'error getting circles by user'}), 400

@circles_bp.route('/add', methods=['PUT'])
@jwt_required()
@add_circle_middleware
def add_circle():
    try:
        # check if user creating circle is logged in user
        claims = get_jwt()
        logged_in_user_id = claims['id']
        host_id = request.json.get('host_id')

        if request.method == 'PUT' and logged_in_user_id == int(host_id):
            conn = connect_db()

            if not conn:
                return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
            
            with conn.cursor() as cur:
                title = request.json.get('title')
                description = request.json.get('description')
                participants_limit = request.json.get('participants_limit', 100)
                start_date = request.json.get('start_date')

                cur.execute("""
                            INSERT INTO circles(host_id, title, description, participants_limit, start_date)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING *
                            """, (host_id, title, description, participants_limit, start_date))
                
                inserted_row = cur.fetchone()

                conn.commit()  
            return jsonify({ 'status': 'ok', 'msg': 'circle created', 'data': inserted_row }), 200
        else:
            return jsonify({ 'status': 'error', 'error': 'creation of new circle unauthorized' }), 403
    except:
        return jsonify({ 'status': 'error', 'msg': 'error creating circle'}), 400

@circles_bp.route('/edit', methods=['PATCH'])
@jwt_required()
@update_circle_middleware
def edit_circle():
    try:
        claims = get_jwt()
        logged_in_user_id = claims['id']

        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            circle_id = request.json.get('circle_id')
            cur.execute("""
                        SELECT * FROM circles
                        WHERE id = %s
                        """, (circle_id,))
            circle = cur.fetchone()

            # check if logged_in_user is host
            if not circle:
                return jsonify({ 'status': 'error', 'msg': 'no circle found' }), 400
            elif logged_in_user_id != circle['host_id']:
                return jsonify({ 'status': 'error', 'msg': 'edit circle unauthorized'}), 403
            
            title = request.json.get('title') or circle['title']
            description = request.json.get('description') or circle['description']
            participants_limit = request.json.get('participants_limit') or circle['participants_limit']
            start_date = request.json.get('start_date') or circle['start_date']
            is_live = request.json.get('is_live') or circle['is_live']
            is_ended = request.json.get('is_ended') or circle['is_ended']

            cur.execute("""
                        UPDATE circles
                        SET title = %s, description = %s, participants_limit = %s, start_date = %s, is_live = %s, is_ended = %s
                        WHERE id = %s
                        """, (title, description, participants_limit, start_date, is_live, is_ended, circle_id))
            conn.commit()
        return jsonify({ 'status': 'ok', 'msg': 'successfully edited circle'}), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to edit circle'}), 400

@circles_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_circle():
    try:
        claims = get_jwt()
        logged_in_user_id = claims['id']
        logged_in_user_role = claims['role']

        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            circle_id = request.json.get('circle_id')
            cur.execute("""
                        SELECT host_id FROM circles
                        WHERE id = %s
                        """, (circle_id,))
            circle = cur.fetchone()

            # check if logged in user is circle host or admin
            if not circle:
                return jsonify({ 'status': 'error', 'msg': 'no circle found' }), 400
            elif logged_in_user_id != circle['host_id'] and logged_in_user_role != 'admin':
                return jsonify({ 'status': 'error', 'msg': 'delete circle unauthorized'}), 403
            
            cur.execute("""
                        DELETE FROM circles
                        WHERE id = %s
                        """, (circle_id,))
            
            conn.commit()
        return jsonify({ 'status': 'ok', 'msg': 'circle deleted'}), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to delete circle'}), 400

@circles_bp.route('/register', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_registration():
    try:
        claims = get_jwt()
        logged_in_user_id = claims['id']
        
        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            circle_id = request.json.get('circle_id')

            if request.method == 'PUT':
                cur.execute("""
                            INSERT INTO circles_registrations(circle_id, user_id)
                            VALUES (%s, %s)
                            """, (circle_id, logged_in_user_id))
                conn.commit()
                return jsonify({ 'status': 'ok', 'msg': 'successfully registered for circle' }), 200
            elif request.method == 'DELETE':
                cur.execute("""
                            DELETE FROM circles_registrations
                            WHERE circle_id = %s AND user_id = %s
                            """, (circle_id, logged_in_user_id))
                conn.commit()
                return jsonify({ 'status': 'ok', 'msg': 'successfully deregistered for circle' }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to manage registration'}), 400

@circles_bp.route('/registrations', methods=['POST'])
@jwt_required()
def get_registered_users():
    try:     
        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            circle_id = request.json.get('circle_id')

            cur.execute("""
                        SELECT users.id, users.username FROM circles_registrations
                        JOIN users ON circles_registrations.user_id = users.id
                        WHERE circles_registrations.circle_id = %s
                        """, (circle_id,))
            data = cur.fetchall()
        return jsonify({ 'status': 'ok', 'msg': 'successfully fetched all registrations', 'data': data }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to get registrations'}), 400

@circles_bp.route('/registered', methods=['GET'])
@jwt_required()
def get_registered_circles():
    try:
        claims = get_jwt()
        logged_in_user_id = claims['id']

        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT circles.*, users.username FROM circles_registrations
                        JOIN circles ON circles_registrations.circle_id = circles.id
                        JOIN users ON circles.host_id = users.id
                        WHERE circles_registrations.user_id = %s
                        ORDER BY circles.start_date
                        """, (logged_in_user_id,))
            data = cur.fetchall()
        return jsonify({ 'status': 'ok', 'msg': 'successfully fetched all circles registered for', 'data': data }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to get circles registered for'}), 400

# Tags endpoints
@circles_bp.route('/tags', methods=['POST'])
@jwt_required()
def get_tags_by_circle():
    try:
        if request.method == 'POST':
            conn = connect_db()

            if not conn:
                return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404

            with conn.cursor() as cur:
                circle_id = request.json.get('circle_id')
                cur.execute("""
                            SELECT tag FROM circle_tags
                            WHERE circle_id = %s
                            """, (circle_id,))
                results = cur.fetchall()
                data = []
                for tag in results:
                    data.append(tag['tag'])
            return jsonify({ 'status': 'ok', 'msg': 'succesfully fetched tags', 'data': data }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to get tags for circle'}), 400
    
@circles_bp.route('/tags/all')
@jwt_required()
def get_all_tags():
    try:
        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tags")
            results = cur.fetchall()
            data = []
            for tag in results:
                data.append(tag['tag'])
        return jsonify({ 'status': 'ok', 'msg': 'succesfully fetched all tags', 'data': data }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to get all tags'}), 400

@circles_bp.route('/tags', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_tags():
    try:
        claims = get_jwt()
        logged_in_user_id = claims['id']

        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            circle_id = request.json.get('circle_id')
            cur.execute("""
                        SELECT host_id FROM circles
                        WHERE id = %s
                        """, (circle_id,))
            circle = cur.fetchone()

            # check if logged_in_user is host
            if not circle:
                return jsonify({ 'status': 'error', 'msg': 'no circle found' }), 400
            elif logged_in_user_id != circle['host_id']:
                return jsonify({ 'status': 'error', 'msg': 'manage tag unauthorized'}), 403

            tag = request.json.get('tag')

            if request.method == 'PUT':
                # refactor to loop through an array for future enhancement
                cur.execute("""
                            INSERT INTO circle_tags(circle_id, tag)
                            VALUES (%s, %s)
                            """, (circle_id, tag))
                conn.commit()
                return jsonify({ 'status': 'ok', 'msg': 'tag(s) added' }), 200
            elif request.method == 'DELETE':
                cur.execute("""
                            DELETE FROM circle_tags
                            WHERE circle_id = %s AND tag = %s
                            """, (circle_id, tag))
                conn.commit()
                return jsonify({ 'status': 'ok', 'msg': 'tag deleted'}), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'manage tag error'}), 400

# Flags endpoints
@circles_bp.route('/flags', methods=['PUT'])
@jwt_required()
def add_flag():
    try:
        claims = get_jwt()
        logged_in_user_id = claims['id']

        if request.method == 'PUT':
            conn = connect_db()

            if not conn:
                return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404

            with conn.cursor() as cur:
                circle_id = request.json.get('circle_id')

                cur.execute("""
                            INSERT INTO flags(circle_id, flag_user_id)
                            VALUES (%s, %s)
                            """, (circle_id, logged_in_user_id))
                conn.commit()
            return jsonify({ 'status': 'ok', 'msg': 'flag successfully created'}), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to add flag'}), 400

@circles_bp.route('/flags', methods=['POST'])
@jwt_required()
def get_flags_by_circle():
    try:
        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404

        with conn.cursor() as cur:
            circle_id = request.json.get('circle_id')

            cur.execute("""
                        SELECT * FROM flags
                        WHERE circle_id = %s
                        """, (circle_id,))
            data = cur.fetchall()
        return jsonify({ 'status': 'ok', 'msg': 'successfully fetched all flags', 'data': data }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to fetch flags'}), 400

@circles_bp.route('/flag', methods=['DELETE'])
@jwt_required()
def delete_flag_by_user():
    try:
        claims = get_jwt()
        logged_in_user_id = claims['id']

        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            circle_id = request.json.get('circle_id')
            cur.execute("""
                        DELETE FROM flags
                        WHERE circle_id = %s AND flag_user_id = %s
                        """, (circle_id,logged_in_user_id))
            conn.commit()
            return jsonify({ 'status': 'ok', 'msg': 'successfully deleted flag' }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to delete flag'}), 400

@circles_bp.route('/flags', methods=['GET', 'DELETE'])
@jwt_required()
def manage_flags():
    try:
        conn = connect_db()

        if not conn:
            return jsonify({ 'status': 'error', 'msg': 'cannot access db'}), 404
        
        with conn.cursor() as cur:
            if request.method == 'GET':
                cur.execute("""
                            SELECT circles.*, users.username, COUNT(circles.id) AS flag_count FROM circles
	                        JOIN flags ON flags.circle_id = circles.id
                            JOIN users ON circles.host_id = users.id
                            GROUP BY circles.id, users.username
                            ORDER BY flag_count DESC
                            """)
                data = cur.fetchall()
                return jsonify({ 'status': 'ok', 'msg': 'successfully fetched all flagged circles', 'data': data }), 200
            elif request.method == 'DELETE':
                circle_id = request.json.get('circle_id')
                cur.execute("""
                            DELETE FROM flags
                            WHERE circle_id = %s
                            """, (circle_id,))
                conn.commit()
                return jsonify({ 'status': 'ok', 'msg': 'successfully deleted all flags relating to a circle' }), 200
    except:
        return jsonify({ 'status': 'error', 'msg': 'unable to manage flag(s)'}), 400