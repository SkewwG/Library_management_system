from django.test import TestCase

# Create your tests here.
a = dict(a=1,b=2,c=3)
for key in a:
    print(key, a[key])