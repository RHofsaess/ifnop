FROM gitlab-registry.cern.ch/linuxsupport/alma9-base:latest

MAINTAINER Robin Hofsaess <Robin.Hofsaess@kit.edu>

RUN dnf -y update && dnf -y clean all

# add EPEL
RUN dnf install -y 'dnf-command(config-manager)' 
RUN dnf config-manager --set-enabled crb
RUN dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm

# Monitoring stuff
# RUN dnf install -y nc net-tools  # debugging

# other packages
RUN dnf install -y vim
RUN dnf install -y python3.9-pip

# Set the working directory in the container
WORKDIR /ifnop

# Copy the current directory contents into the container at /app
ADD . /ifnop


RUN ./setup.sh

# Run with config
#CMD ["python", "main.py", "--config", "config_prod.ini"]
CMD ["sleep", "1000"]
