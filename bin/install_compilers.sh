#!/usr/bin/env bash
#set -ex


# GCC cross compilers
while read prefix libpfm4_arch extra_packages; do
    (

	package_suffix=$(echo $prefix | sed 's/_/-/g;' )
	apt-get install -y g++-$package_suffix gcc-$package_suffix binutils-$package_suffix || exit 0 # it's ok to fail here.  we just skip it

	if [ x"$extra_packages" != x ]; then
	    apt-get install -y $extra_packages
	fi
	
	export CXX=$prefix-g++
	export CC=$prefix-gcc

	cd /tmp
	rm -rf libpfm4;
	git clone http://github.com/wcohen/libpfm4.git
	cd libpfm4
	make PREFIX=/usr/$($CC -print-multiarch) ARCH=$libpfm4_arch lib install
    )
done <<EOF
powerpc-linux-gnu powerpc 
x86_64-linux-gnu x86_64 
arm-linux-gnueabi arm g++-8-arm-linux-gnueabi gcc-8-arm-linux-gnueabi
EOF

##### Go 
apt-get install -y golang-go
##### Clang
apt-get install -y clang clang-11 lld # need these for modern clang cross-compiler support.

exit 0

