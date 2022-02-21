# This is an example PKGBUILD file. Use this as a start to creating your own,
# and remove these comments. For more information, see 'man PKGBUILD'.
# NOTE: Please fill out the license field for your package! If it is unknown,
# then please put 'unknown'.

# Maintainer: RickrollMaster101 rickrollmaster101@protonmail.com
pkgname=about-this-pear
pkgver=1.0.0
pkgrel=1
pkgdesc="About this mac clone for pearOS"
arch=('x86_64')
url="https://github.com/RickRollMaster101/About-This-Pearintosh"
license=('GPL')
depends=('python3')
source=("About-This-Pearintosh.tar.gz")

prepare() {
	cd "About-This-Pearintosh"
}


check() {
    echo soon
}

package() {
	cd "About-This-Pearintosh"

    pip install numpy


    if [ ! -f /home/`whoami`/.local/bin ]; then
        mkdir -p /home/`whoami`/.local/bin
    fi

    mv about-this-pear.py /home/`whoami`/.local/bin/about-this-pear
    cd /home/`whoami`/.local/bin
    chmod +x about-this-pear
    cd -
}
