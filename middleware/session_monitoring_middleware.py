# session_monitoring_middleware.py

import datetime

class SessionMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Логуємо час входу користувача
        login_time = datetime.datetime.now()
        
        response = self.get_response(request)
        
        # Логуємо час виходу користувача та тривалість сесії
        logout_time = datetime.datetime.now()
        session_duration = logout_time - login_time
        
        # Зберігаємо дані про сесію в файл
        with open('session_logs.txt', 'a') as file:
            file.write(f"User: {request.user}, Login Time: {login_time}, Logout Time: {logout_time}, Session Duration: {session_duration}\n")

        return response
