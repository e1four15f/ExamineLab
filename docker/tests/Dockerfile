FROM chug/ubuntu14.04x64
WORKDIR /ExamineLab/modules
RUN echo "deb http://archive.ubuntu.com/ubuntu trusty main universe" > /etc/apt/sources.list
RUN apt-get update

# C/C++
RUN apt-get install -y gcc

# C#
RUN apt-get install -y mono-xsp2 mono-xsp2-base

# PHP
RUN apt-get install -y php5-cli

# Python
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.7
RUN apt-get -y install python3-pip
RUN pip3 install numpy
RUN alias python3="python3.7"

# JavaScript
RUN apt-get install -y npm	
RUN apt-get install -y nodejs

#Java
RUN apt-get install openjdk-7-jre
