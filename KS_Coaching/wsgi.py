import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KS_Coaching.settings')

application = get_wsgi_application()

# Add this line for Vercel serverless integration
app = application