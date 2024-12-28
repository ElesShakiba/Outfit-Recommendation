from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# تنظیمات دیتابیس
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///outfit_recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# مدل‌ها (تعریف جداول)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    size = db.Column(db.String(5), nullable=False)
    style_preferences = db.Column(db.String(200), nullable=False)
    favorite_colors = db.Column(db.String(200))

class Clothes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(5), nullable=False)
    material = db.Column(db.String(100), nullable=False)
    style = db.Column(db.String(100), nullable=False)

class OutfitSuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    clothes_ids = db.Column(db.String(500), nullable=False)  # نگهداری به صورت کاما جدا شده
    weather_condition = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())



# الگوریتم پیشنهاد لباس
def suggest_outfit(user_id, weather_condition, temperature):
    user = User.query.get(user_id)
    if not user:
        return "User not found"

    # فیلتر لباس‌ها بر اساس آب‌وهوا
    if temperature < 15:
        clothes = Clothes.query.filter(Clothes.material.in_(['wool', 'fleece'])).all()
    elif temperature > 25:
        clothes = Clothes.query.filter(Clothes.material.in_(['cotton', 'linen'])).all()
    else:
        clothes = Clothes.query.all()

    # فیلتر بر اساس ترجیحات کاربر
    filtered_clothes = [c for c in clothes if c.size == user.size and c.style in user.style_preferences]

    # ست کردن لباس‌ها
    suggestions = {
        "top": next((c for c in filtered_clothes if c.type == 'top'), None),
        "bottom": next((c for c in filtered_clothes if c.type == 'bottom'), None),
        "shoes": next((c for c in filtered_clothes if c.type == 'shoes'), None)
    }

    return suggestions

@app.route('/suggest/<int:user_id>/<string:weather_condition>/<float:temperature>')
def suggest(user_id, weather_condition, temperature):
    result = suggest_outfit(user_id, weather_condition, temperature)
    return jsonify(result)


# افزودن کاربران
def add_test_data():
    user1 = User(
        name="Ali",
        gender="Male",
        size="M",
        style_preferences="casual,formal",
        favorite_colors="blue,black"
    )
    user2 = User(
        name="Sara",
        gender="Female",
        size="S",
        style_preferences="sporty,casual",
        favorite_colors="red,white"
    )
    
    # افزودن لباس‌ها
    clothes = [
        Clothes(type="top", color="blue", size="M", material="cotton", style="casual"),
        Clothes(type="bottom", color="black", size="M", material="denim", style="casual"),
        Clothes(type="shoes", color="white", size="M", material="leather", style="formal"),
        Clothes(type="top", color="red", size="S", material="wool", style="sporty"),
        Clothes(type="bottom", color="white", size="S", material="cotton", style="sporty"),
        Clothes(type="shoes", color="black", size="S", material="rubber", style="casual"),
    ]

    db.session.add(user1)
    db.session.add(user2)
    db.session.add_all(clothes)
    db.session.commit()

    print("Test data added successfully!")
    
    

# اجرای برنامه
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # ساخت جداول در دیتابیس
    app.run(debug=True)
