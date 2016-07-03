# Development

Download the latest Arch Linux image from [https://www.archlinux.org/download/](https://www.archlinux.org/download/)

After loading the image onto a machine, run:

    $repo/scripts/installation.sh
    arch-chroot /mnt
    $repo/scripts/setup.sh

Then reboot:

    exit
    umount -R /mnt
    reboot
