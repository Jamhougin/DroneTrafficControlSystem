#!/bin/bash

## Name:        James Hall
## Student No:  C00007006
## Institute:   Institute of Technology Carlow
## Project:     Drone Traffic Control System     
## Date:        April 2021 
## License:     GNU Affero General Public License v3.0

sudo apt-get update

echo ""
echo "$(tput setaf 2)$(tput bold)[Installing Python 3.6:]$(tput sgr 0)"
sudo apt-get install python3.6

echo ""
echo "$(tput setaf 4)$(tput bold)[Installing Pip:]$(tput sgr 0)"
sudo apt install python3-pip

cwd=$(pwd)
echo $cwd

echo ""
echo "$(tput setaf 7)$(tput bold)[Installing virtualev:]$(tput sgr 0)"
sudo apt install virtualenv
mkdir ~/python-env
cd ~/python-env
virtualenv ADTCS
virtualenv --python=python3 ADTCS

echo ""
echo "$(tput setaf 5)$(tput bold)[Activating environment:]$(tput sgr 0)"
source ~/python-env/ADTCS/bin/activate

echo ""
echo "$(tput setaf 8)$(tput bold)[Installing requirements:]$(tput sgr 0)"
cd $cwd
cd ..
python3 -m pip install -r requirements.txt


