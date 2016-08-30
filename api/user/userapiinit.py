from api.apiconfig import app
import api.user.relationshipapi
import api.user.userapi
import api.user.membershipapi
from dbmodel.database_init import create_database

create_database()

if __name__ == '__main__':
    app.run(debug=True)
