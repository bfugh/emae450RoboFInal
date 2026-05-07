import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/awudali/enae450_final/emae450RoboFInal/turtlebot4_ws/install/turtlebot4_diagnostics'
