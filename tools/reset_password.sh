docker exec -it 08f9dc7d46c9 /bin/bash
export FLASK_APP=api.apps
flask reset-password --email 27@qq.com --new-password admin123 --password-confirm admin123
