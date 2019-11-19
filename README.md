# nham
NFV High-Availability Module

#requirements
- docker running
- docker experimental flag
sudo vim /etc/docker/daemon.json
{
"experimental": true
}
sudo service docker restart

- CRIU
sudo apt-get install criu

pip install pyyaml docker

mkdir db
touch db/...
