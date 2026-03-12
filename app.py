from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# [중요] 기존 SQLite 설정을 지우고 아래와 같이 변경합니다.
# Render의 환경변수 DATABASE_URL을 사용하거나, 직접 주소를 입력합니다.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '여기에_복사한_External_URL_붙여넣기')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 장비 및 재고 모델 (기존과 동일) ---
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

# DB 테이블 생성 및 초기화
with app.app_context():
    db.create_all()
    if Part.query.count() < 10:
        parts_data = [
            ("모터 좌측 세트", 1), ("모터 우측 세트", 0), ("조명 세트", 0),
            ("ESC 우측 세트", 6), ("ESC 좌측 세트", 5), 
            ("CT200", 18), ("CTM300", 3), ("그리퍼", 2), 
            ("어뢰", 6), ("연구소 소모품", 0)
        ]
        for name, qty in parts_data:
            db.session.add(Part(name=name, quantity=qty))
        db.session.commit()

# --- 라우팅 함수들 (기존 v8.2 로직 유지) ---
# @app.route('/') ... @app.route('/add') ... 등등

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
