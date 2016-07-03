#!/bin/bash

# Update local time
timedatectl set-ntp true

# Create partitions
parted /dev/sda -s mklabel msdos
parted /dev/sda -s mkpart primary ext4 1MiB 100MiB
parted /dev/sda -s set 1 boot on
parted /dev/sda -s mkpart primary ext4 100MiB 100%

# Encrypt and mount root partition (/dev/sda2)
read -s -p "Disk encryption Password: " encryption_password ; echo ""
echo -n $encryption_password | cryptsetup -y -v luksFormat /dev/sda2 -
echo -n $encryption_password | cryptsetup open /dev/sda2 cryptroot -
mkfs -t ext4 /dev/mapper/cryptroot
mount -t ext4 /dev/mapper/cryptroot /mnt

# Mount boot partition
mkfs -t ext4 /dev/sda1
mkdir /mnt/boot
mount -t ext4 /dev/sda1 /mnt/boot

# Update Pacman mirror list
mv /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.old
curl "https://www.archlinux.org/mirrorlist/?country=US&protocol=http&ip_version=4&use_mirror_status=on" -o /etc/pacman.d/mirrorlist
sed -i "/#Server/s/^#//g" /etc/pacman.d/mirrorlist

# Install base and base-devel packages
pacstrap /mnt base base-devel

# Generate fstab
genfstab -p /mnt >> /mnt/etc/fstab
