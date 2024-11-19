from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    # CORS 설정을 조금 더 명확하게
    CORS(app, resources={r"/api/*": {"origins": "*"}})  # 필요한 경우 origins에 특정 도메인을 추가

    from app.routes import main
    app.register_blueprint(main)

    return app

# 애플리케이션 실행 코드 추가
if __name__ == '__main__':
    app = create_app()
    app.run(port=5000)  # 포트 번호를 지정하여 실행