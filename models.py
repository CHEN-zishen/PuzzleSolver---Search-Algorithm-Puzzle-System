from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_levels = db.Column(db.String(500), default="[]")
    
    def get_completed_levels(self):
        import json
        return json.loads(self.completed_levels)
    
    def add_completed_level(self, level_id):
        completed = self.get_completed_levels()
        if level_id not in completed:
            completed.append(level_id)
            self.completed_levels = json.dumps(completed)
            db.session.commit()
    
    def has_completed_level(self, level_id):
        return level_id in self.get_completed_levels()
    
    def can_access_level(self, level_id):
        # 所有关卡都开放，不锁定
        return True

class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    puzzle_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    puzzle_data = db.Column(db.Text)
    hints = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'puzzle_type': self.puzzle_type,
            'difficulty': self.difficulty,
            'description': self.description,
            'order': self.order
        }

class SolveRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    algorithm = db.Column(db.String(50), nullable=False)
    steps = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Float, nullable=False)
    solved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('solve_records', lazy=True))
    level = db.relationship('Level', backref=db.backref('solve_records', lazy=True))
