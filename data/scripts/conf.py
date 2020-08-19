# Locale
locale = 'en'

# URL-s
if locale == 'et':
    host = 'https://www.autodoc.ee'
    cats_main = host + '/auto-osad'
    tyres = host + '/rehvid/'
    tyres_list = tyres + '/type_list'
else:
    host = 'https://www.autodoc.co.uk'
    cats_main = host + '/car-parts'
    tyres = host + '/tyres/'
    tyres_list = tyres + '/type_list'