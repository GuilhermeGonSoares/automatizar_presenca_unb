
from app.models import User
from app import init_app
#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    app = init_app()
    app.run(debug=True)