from flask import request
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from securities.security import auth_by_token
from controllers.post import PostController, PostListController

class Post(Resource):
    """
    /posts
    used for creating posts
    """
    parser = reqparse.RequestParser()
    parser.add_argument('theme',
            type=str,
            required=True,
            help="This field is required and cannot be left blank."
    )
    parser.add_argument('anonymity',
            type=str,
            required=True,
            help="This field is required and cannot be left blank."
    )
    parser.add_argument('content',
            type=str,
            required=True,
            help="This field is required and cannot be left blank."
    )

    def post(self):
        data = Post.parser.parse_args()

        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header.split(" ")[1]
        else:
            return {"message": "This method requires an authorization header."}, 400
        error, client_id = auth_by_token(access_token)
        if error:
            return {"message": error}, 401

        error_message = PostController.create_post(data['theme'], data['anonymity'], client_id, data['content'])
        if error_message:
            return {"message": error_message}, 400

        return {"message":"Success!"}, 201


class PostList(Resource):
    """
    postlist/<mode>/<key>
    get: retrieves post(s) by theme, user, or by most saved
    post: retrievs posts by list of ids given

    """
    parser = reqparse.RequestParser()
    parser.add_argument('wanted',
            type=str,
            required=True,
            help="List of ids of posts wanted."
    )

    def get(self, mode, key):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header.split(" ")[1]
        else:
            return {"message": "This method requires an authorization header."}, 400
        error, client_id = auth_by_token(access_token)
        if error:
            return {"message": error}, 401

        error_message = ""

        if safe_str_cmp(mode, 'theme'):
            error_message, response = PostListController.filter_by_theme(key)
        elif safe_str_cmp(mode, 'user'):
            error_message, response = PostListController.filter_by_writer_id(key)
        elif safe_str_cmp(mode, 'saved'):
            error_message, response = PostListController.filter_by_most_saved(key)
        else:
            error_message = "Wrong mode. Try theme, user, or saved"

        if error_message:
            return {"message": error_message}, 400

        return {"response": list(map(lambda x: x.json() if x else None, response))}

    def post(self, mode, key):
        data = PostList.parser.parse_args()

        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header.split(" ")[1]
        else:
            return {"message": "This method requires an authorization header."}, 400
        error, client_id = auth_by_token(access_token)
        if error:
            return {"message": error}, 401

        error_message = "Wrong mode or key."

        if safe_str_cmp(mode, 'id') and safe_str_cmp(key, "please"):
            error_message, response = PostListController.filter_by_id(data['wanted'])

        if error_message:
            return {"message": error_message}, 400

        return {"response": list(map(lambda x: x.json() if x else None, response))}

    @jwt_required()
    def delete(self, key):
        wanted_post = find_by_id(key)

        if current_identity.username == wanted_post.username:
            wanted_post.delete_from_db()
        else:
            return {'message': 'Only the writer of the post can delete the post'}, 400

        return {'message': 'Post has been successfully deleted'}

