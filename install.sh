if [ ! -f /usr/bin/python3 ]; then
    if [ -f /etc/debian_version ]; then
        sudo apt-get install -y python3
        elif [ -f /etc/redhat-release ]; then
        sudo yum install python3
        elif [ -f /etc/arch-release ]; then
        sudo pacman -Sy --noconfirm python3
        elif [ -f /etc/gentoo-release ]; then
        sudo emerge python3
        elif [ -f /etc/SuSE-release ]; then
        sudo zypper install python3
        elif [ -f /etc/fedora-release ]; then
        sudo dnf install python3
        elif [ -f /etc/slackware-version ]; then
        sudo slackpkg install python3
        elif [ -f /etc/alpine-release ]; then
        sudo apk add python3
        elif [ -f /etc/centos-release ]; then
        sudo yum install python3
        elif [ -f /etc/nixos ]; then
        sudo nix-env -iA python3
    fi
fi

pip install numpy

python3 about-this-pear.py 

if [ ! -f /home/`whoami`/.local/bin ]; then
    mkdir -p /home/`whoami`/.local/bin
fi

cp about-this-pear.py /home/`whoami`/.local/bin/about-this-pear
cd /home/`whoami`/.local/bin
chmod +x about-this-pear
cd -
echo You may need to add /home/`whoami`/.local/bin to your '$PATH' environment variable
