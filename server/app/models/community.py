"""
Community models.
CommunityPost: a shared trip experience/recommendation posted by a user,
optionally linked to one of their Trips (e.g. "Copy Trip" provenance).
CommunityComment / CommunityLike: engagement primitives for the feed.
"""
from datetime import datetime

from app.extensions import db


class CommunityPost(db.Model):
    __tablename__ = "community_posts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=True)

    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(80), nullable=True)  # e.g. city/topic tag for grouping
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comments = db.relationship(
        "CommunityComment", backref="post", lazy=True, cascade="all, delete-orphan"
    )
    likes = db.relationship(
        "CommunityLike", backref="post", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user": self.author.to_dict() if self.author else None,
            "trip_id": self.trip_id,
            "content": self.content,
            "image_url": self.image_url,
            "category": self.category,
            "comment_count": len(self.comments),
            "like_count": len(self.likes),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CommunityComment(db.Model):
    __tablename__ = "community_comments"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("community_posts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "post_id": self.post_id,
            "user": self.author.to_dict() if self.author else None,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CommunityLike(db.Model):
    __tablename__ = "community_likes"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("community_posts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("post_id", "user_id", name="uq_post_like_per_user"),
    )
