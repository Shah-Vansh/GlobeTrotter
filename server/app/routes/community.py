"""
Community routes.
Feed of shared trip experiences with search/filter/sort/group, plus
comment and like interactions (Community Page spec).
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from app.extensions import db
from app.models import CommunityPost, CommunityComment, CommunityLike
from app.utils.responses import success, error

community_bp = Blueprint("community", __name__)


def _current_user_id_optional():
    """Best-effort viewer id: returns None for anonymous/invalid tokens
    instead of raising, so the public feed still renders for guests.
    JWT identities are stored as strings (see auth.py's create_access_token
    calls), so this converts back to int for comparison against
    CommunityLike.user_id."""
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return int(identity) if identity is not None else None
    except Exception:
        return None


@community_bp.route("/posts", methods=["GET"])
def list_posts():
    """GET /api/community/posts?search=&category=&sort_by=recent|popular&group_by=category"""
    viewer_id = _current_user_id_optional()
    query = CommunityPost.query

    search = request.args.get("search")
    if search:
        query = query.filter(CommunityPost.content.ilike(f"%{search}%"))

    category = request.args.get("category")
    if category:
        query = query.filter(CommunityPost.category.ilike(category))

    sort_by = request.args.get("sort_by", "recent")
    posts = query.all()
    if sort_by == "popular":
        posts.sort(key=lambda p: len(p.likes), reverse=True)
    else:
        posts.sort(key=lambda p: p.created_at, reverse=True)

    group_by = request.args.get("group_by")
    if group_by == "category":
        groups = {}
        for p in posts:
            groups.setdefault(p.category or "General", []).append(p.to_dict(viewer_id))
        return success({"groups": groups})

    return success([p.to_dict(viewer_id) for p in posts])


@community_bp.route("/posts", methods=["POST"])
@jwt_required()
def create_post():
    """POST /api/community/posts  body/form: { content, category?, trip_id? }, file: image"""
    user_id = get_jwt_identity()
    data = request.form if request.form else (request.json or {})

    if not data.get("content"):
        return error("content is required.", 400)

    image_url = None
    if "image" in request.files:
        from app.utils.cloudinary_utils import upload_image

        image_url = upload_image(request.files["image"], folder="globetrotter/community")

    post = CommunityPost(
        user_id=user_id,
        trip_id=data.get("trip_id") or None,
        content=data["content"],
        category=data.get("category"),
        image_url=image_url,
    )
    db.session.add(post)
    db.session.commit()
    return success(post.to_dict(viewer_id=user_id), message="Post shared.", status_code=201)


@community_bp.route("/posts/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    """DELETE /api/community/posts/<id> - author only."""
    user_id = get_jwt_identity()
    post = CommunityPost.query.filter_by(id=post_id, user_id=user_id).first()
    if not post:
        return error("Post not found or not owned by you.", 404)
    db.session.delete(post)
    db.session.commit()
    return success(message="Post deleted.")


@community_bp.route("/posts/<int:post_id>/comments", methods=["GET"])
def list_comments(post_id):
    """GET /api/community/posts/<id>/comments"""
    post = CommunityPost.query.get(post_id)
    if not post:
        return error("Post not found.", 404)
    return success([c.to_dict() for c in post.comments])


@community_bp.route("/posts/<int:post_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(post_id):
    """POST /api/community/posts/<id>/comments  body: { content }"""
    user_id = get_jwt_identity()
    post = CommunityPost.query.get(post_id)
    if not post:
        return error("Post not found.", 404)

    content = (request.json or {}).get("content")
    if not content:
        return error("content is required.", 400)

    comment = CommunityComment(post_id=post.id, user_id=user_id, content=content)
    db.session.add(comment)
    db.session.commit()
    return success(comment.to_dict(), message="Comment added.", status_code=201)


@community_bp.route("/posts/<int:post_id>/like", methods=["POST"])
@jwt_required()
def toggle_like(post_id):
    """POST /api/community/posts/<id>/like - toggles like on/off for the current user."""
    user_id = get_jwt_identity()
    post = CommunityPost.query.get(post_id)
    if not post:
        return error("Post not found.", 404)

    existing = CommunityLike.query.filter_by(post_id=post.id, user_id=user_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return success({"liked": False, "like_count": len(post.likes)}, message="Like removed.")

    like = CommunityLike(post_id=post.id, user_id=user_id)
    db.session.add(like)
    db.session.commit()
    return success({"liked": True, "like_count": len(post.likes)}, message="Post liked.")
