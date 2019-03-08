#!/bin/bash
tmpdir='/tmp'
AURdir=ssh://aur@aur.archlinux.org/$1.git
ver=$2

export GIT_COMMITTER_NAME=NUCon
export GIT_COMMITTER_EMAIL=me@mail.caref.xyz

cd $tmpdir
workdir=$(mktemp -d AURupdate.XXXX)
cd $workdir

# Exit when any command fail
set -e
git clone $AURdir
cd $1
sed -i "/pkgver=/cpkgver=$ver" PKGBUILD
sed -i "/md5sums/c$(makepkg -g)" PKGBUILD
makepkg --printsrcinfo > .SRCINFO
git commit PKGBUILD .SRCINFO -m "update to v$ver" --author="CareF <CareF.Lm@gmail.com>"
# git push
cd $tmpdir
rm -rf $workdir
