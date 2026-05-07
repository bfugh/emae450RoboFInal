#include <chrono>
#include <memory>

#include <SDL2/SDL.h>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"

using namespace std::chrono_literals;

class Tb4Controller : public rclcpp::Node
{
public:
    Tb4Controller() : Node("tb4_controller")
    {
        publisher_ = this->create_publisher<geometry_msgs::msg::TwistStamped>(
            "tb4_5/cmd_vel",
            10
        );

        if (SDL_Init(SDL_INIT_VIDEO) < 0) {
            RCLCPP_ERROR(this->get_logger(), "SDL could not initialize: %s", SDL_GetError());
            rclcpp::shutdown();
            return;
        }

        window_ = SDL_CreateWindow(
            "TurtleBot4 SDL Teleop",
            SDL_WINDOWPOS_CENTERED,
            SDL_WINDOWPOS_CENTERED,
            500,
            300,
            SDL_WINDOW_SHOWN
        );

        if (window_ == nullptr) {
            RCLCPP_ERROR(this->get_logger(), "SDL window could not be created: %s", SDL_GetError());
            SDL_Quit();
            rclcpp::shutdown();
            return;
        }

        timer_ = this->create_wall_timer(
            50ms,
            std::bind(&Tb4Controller::timer_callback, this)
        );

        RCLCPP_INFO(this->get_logger(), "SDL TurtleBot controller started.");
        RCLCPP_INFO(this->get_logger(), "Click the SDL window, then hold W/A/S/D to move.");
    }

    ~Tb4Controller()
    {
        if (window_ != nullptr) {
            SDL_DestroyWindow(window_);
            window_ = nullptr;
        }

        SDL_Quit();
    }

private:
    void process_sdl_events()
    {
        SDL_Event event;

        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                RCLCPP_INFO(this->get_logger(), "SDL window closed. Shutting down.");
                rclcpp::shutdown();
            }

            if (event.type == SDL_KEYDOWN && event.key.repeat == 0) {
                if (event.key.keysym.sym == SDLK_w) {
                    w_down_ = true;
                } else if (event.key.keysym.sym == SDLK_s) {
                    s_down_ = true;
                } else if (event.key.keysym.sym == SDLK_a) {
                    a_down_ = true;
                } else if (event.key.keysym.sym == SDLK_d) {
                    d_down_ = true;
                } else if (event.key.keysym.sym == SDLK_ESCAPE) {
                    rclcpp::shutdown();
                }
            }

            if (event.type == SDL_KEYUP) {
                if (event.key.keysym.sym == SDLK_w) {
                    w_down_ = false;
                } else if (event.key.keysym.sym == SDLK_s) {
                    s_down_ = false;
                } else if (event.key.keysym.sym == SDLK_a) {
                    a_down_ = false;
                } else if (event.key.keysym.sym == SDLK_d) {
                    d_down_ = false;
                }
            }
        }
    }

    void timer_callback()
    {
        process_sdl_events();

        auto msg = geometry_msgs::msg::TwistStamped();

        msg.header.stamp = this->get_clock()->now();
        msg.header.frame_id = "base_link";

        if (w_down_ && !s_down_) {
            msg.twist.linear.x = 0.2;
        } else if (s_down_ && !w_down_) {
            msg.twist.linear.x = 0.2;
        } else {
            msg.twist.linear.x = 0.0;
        }

        if (a_down_ && !d_down_) {
            msg.twist.angular.z = 0.5;
        } else if (d_down_ && !a_down_) {
            msg.twist.angular.z = -0.5;
        } else {
            msg.twist.angular.z = 0.0;
        }

        publisher_->publish(msg);
    }

    rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr publisher_;

    rclcpp::TimerBase::SharedPtr timer_;

    SDL_Window * window_ = nullptr;

    bool w_down_ = false;
    bool a_down_ = false;
    bool s_down_ = false;
    bool d_down_ = false;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<Tb4Controller>();

    rclcpp::spin(node);

    rclcpp::shutdown();

    return 0;
}