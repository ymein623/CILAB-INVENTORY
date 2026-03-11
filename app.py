from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# DB 설정
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 모델 정의
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    manager = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()
    # 재고 항목을 10개로 업데이트 (항목 수정 및 추가)
    parts_data = [
        ("모터 좌측 세트", 10), ("모터 우측 세트", 10), ("조명 세트", 10),
        ("ESC 우측 세트", 1), ("ESC 좌측 세트", 1), 
        ("CT200", 5), ("CTM300", 3), ("그리퍼", 2), 
        ("어뢰", 4), ("예비 항목", 0) # 10개를 맞추기 위한 예비 항목
    ]
    
    # 기존 데이터가 있어도 10개를 강제로 맞추기 위한 로직
    if Part.query.count() < 10:
        Part.query.delete() # 기존 5개 데이터를 지우고 새로 생성
        for name, qty in parts_data:
            db.session.add(Part(name=name, quantity=qty))
        db.session.commit()

# ... (나머지 API 동일) ...

@app.route('/')
def dashboard():
    return render_template('dashboard.html', items=Equipment.query.all(), parts=Part.query.all())

# --- 장비 API (추가/수정/삭제/상태변경) ---
@app.route('/add', methods=['POST'])
def add_item():
    item = Equipment(status=request.form.get('status'), name=request.form.get('name'), manager=request.form.get('manager'), note=request.form.get('note'))
    db.session.add(item); db.session.commit(); return "OK", 200

@app.route('/update/<int:id>', methods=['POST'])
def update_item(id):
    item = Equipment.query.get(id)
    if item:
        item.status, item.name, item.manager, item.note = request.form.get('status'), request.form.get('name'), request.form.get('manager'), request.form.get('note')
        db.session.commit(); return "OK", 200
    return "Error", 404

@app.route('/delete/<int:id>', methods=['POST'])
def delete_item(id):
    item = Equipment.query.get(id)
    if item: db.session.delete(item); db.session.commit()
    return "OK", 200

@app.route('/update_status', methods=['POST'])
def update_status():
    item = Equipment.query.get(request.form.get('id'))
    if item: item.status = request.form.get('status'); db.session.commit()
    return "OK", 200

# --- 재고 수정 API (신규) ---
@app.route('/update_part', methods=['POST'])
def update_part():
    part = Part.query.get(request.form.get('id'))
    if part:
        part.quantity = int(request.form.get('quantity'))
        db.session.commit(); return "OK", 200
    return "Error", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)