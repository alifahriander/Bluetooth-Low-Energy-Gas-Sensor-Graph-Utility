from setuptools import setup, find_packages

setup(name='CMUT Graph graph Manager',
      version='0.1',
      description='CMUT Graph graph Manager',
      author='Derek Santos',
      url='https://github.com/santosderek/Bluetooth-Low-Energy-Gas-graph-Manager',
      packages=['graph_client'],
      scripts=['graph_client/main.py',
               'graph_client/graph_widget.py',
               'graph_client/graph_widget_threads.py',
               'graph_client/config.py'],
      entry_points={
        'console_scripts':
            ['graphclient = main:main']
      }
     )
