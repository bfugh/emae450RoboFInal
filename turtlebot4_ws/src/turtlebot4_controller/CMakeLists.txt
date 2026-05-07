cmake_minimum_required(VERSION 3.8)
project(turtlebot4_controller)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(SDL2 REQUIRED)

add_executable(turtlebot4_controller src/tb4_controller.cpp)

ament_target_dependencies(turtlebot4_controller
  rclcpp
  geometry_msgs
)

target_include_directories(turtlebot4_controller PRIVATE
  ${SDL2_INCLUDE_DIRS}
)

target_link_libraries(turtlebot4_controller
  ${SDL2_LIBRARIES}
)

install(TARGETS
  turtlebot4_controller
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()