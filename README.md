# Development

Download the latest Arch Linux image from [https://www.archlinux.org/download/](https://www.archlinux.org/download/)

After loading the image onto a machine, run:

    $repo/scripts/installation.sh
    arch-chroot /mnt
    $repo/scripts/setup.sh

Remove the installation media, then reboot:

    exit
    umount -R /mnt
    reboot

Run Ansible:

    cd $repo/ansible
    ansible-playbook site.yaml -i hosts --extra-vars "username=$USERNAME password=$PASSWORD"
