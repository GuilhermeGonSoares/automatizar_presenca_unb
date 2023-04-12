from app.models import User
from app import create_app

app = create_app()
app.run(debug=False)