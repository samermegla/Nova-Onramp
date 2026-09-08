FROM ubuntu:jammy
ENV DEBIAN_FRONTEND=noninteractive

#Locale 
RUN apt-get update && apt-get install -y locales && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8
ENV LANG en_US.UTF-8

#Universe repo
Run apt install -y software-properties-common && \
    add-apt-repository universe

# ROS 2 apt source
RUN apt update && apt install -y curl \
 && export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}') \
 && curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.jammy_all.deb" \
 && dpkg -i /tmp/ros2-apt-source.deb

 # Dev tools
RUN apt update && apt install -y \
      python3-flake8-docstrings python3-pip python3-pytest-cov ros-dev-tools \
 && apt install -y \
      python3-flake8-blind-except python3-flake8-builtins \
      python3-flake8-class-newline python3-flake8-comprehensions \
      python3-flake8-deprecated python3-flake8-import-order \
      python3-flake8-quotes python3-pytest-repeat python3-pytest-rerunfailures
 
# Source checkout
WORKDIR /opt/ros2_humble
RUN mkdir -p src \
 && vcs import --input https://raw.githubusercontent.com/ros2/ros2/humble/ros2.repos src

# Dependencies
RUN apt upgrade -y && rosdep init && rosdep update \
 && rosdep install --from-paths src --ignore-src -y \
      --skip-keys "fastcdr rti-connext-dds-6.0.1 urdfdom_headers"

# Build
RUN colcon build --symlink-install

RUN echo ". /opt/ros2_humble/install/local_setup.bash" >> /root/.bashrc