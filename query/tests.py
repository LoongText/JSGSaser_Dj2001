from django.test import TestCase
import time

# Create your tests here.

# current_time = time.strftime('%H%M%S')
current_date = time.strftime('%Y-%m-%d %H%M%S')


def a():
    print(current_date)
    time.sleep(3)
    print(time.strftime('%Y-%m-%d %H%M%S'))


a()
