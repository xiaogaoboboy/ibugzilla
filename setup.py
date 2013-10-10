from setuptools import find_packages, setup

# name can be any name.  This name will be used to create the .egg file.
# name that is used in packages is the one that is used in the trac.ini file.
# use package name as entry_points
setup(
    name='iData', version='0.1',
    packages=find_packages(exclude=['*.tests*']),
    entry_points = """
        [trac.plugins]
        iData = iData
    """,
    package_data={'iData': ['templates/*.html', 
                                 'htdocs/css/*.css', 
                                 'htdocs/js/*.js',
                                 'htdocs/images/*']},
)
