# experiment-webserver
This repository contains the code to setup the control website, and connect to the Docker daemon and the Kubernetes master.  
It can be installed by running:
```bash
git clone https://github.ugent.be/jlemaes/experiment-webserver.git
cd experiment-webserver
pip install -r requirements.txt
python manage.py migrate
cat > setup_superuser.py <<EOL
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'admin')
EOL
python manage.py shell < setup_superuser.py
python manage.py runserver -6 [::0]:8000
```
After this, the website will be accessible by going to the public IPv6 address of the server.
