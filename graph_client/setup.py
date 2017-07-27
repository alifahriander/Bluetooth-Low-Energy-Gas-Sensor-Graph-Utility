from setuptools import setup, find_packages

setup(name='CMUT Graph graph Manager',
      version='0.1',
      description='CMUT Graph graph Manager',
      author='Derek Santos',
      url='https://github.com/santosderek/Bluetooth-Low-Energy-Gas-graph-Manager',
      packages=['graph_client'],
      scripts=['graph_client/main.py',
               'graph_client/main_window.py',
               'graph_client/graph.py',
               'graph_client/config.py'],
      entry_points={
        'console_scripts':
            ['graphclient = main:main']
      },
      install_requires=['pyqtgraph==0.10.0', 'PyQt5==5.9']
     )
