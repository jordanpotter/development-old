#!/bin/bash

# Set keyboard layout
read -p "Keyboard layout (default=dvorak): " keyboard
keyboard=${keyboard:-dvorak}
loadkeys $keyboard
echo "KEYMAP=$keyboard" > /etc/vconsole.conf

# Set root password
read -s -p "Root user Password: " root_password ; echo ""
echo -e "$root_password\n$root_password" | passwd

# Set hostname
read -p "Hostname: " hostname
echo $hostname > /etc/hostname

# Set timezone
read -p "Timezone (default=America/Los_Angeles): " timezone
timezone=${timezone:-'America/Los_Angeles'}
ln -s /usr/share/zoneinfo/$timezone /etc/localtime

# Set locale
sed -i "/#en_US\.UTF-8/s/^#//g" /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

# Configure mkinitcpio
sed -i "/^HOOKS=/s/filesystems/encrypt filesystems/" /etc/mkinitcpio.conf
mkinitcpio -p linux

# Install boot loader
pacman -S --noconfirm grub
grub-install /dev/sda

# Configure boot loader to decrypt root
root_uuid=$(blkid /dev/sda2 | sed 's/.* UUID="\([a-z0-9-]*\).*/\1/')
kernal_param="cryptdevice=UUID=$root_uuid:cryptroot root=/dev/mapper/cryptroot"
sed_friendly_kernel_param=$(echo $kernal_param | sed 's/\//\\\//g')
sed -i '/^GRUB_CMDLINE_LINUX=/s/"$/ '"$sed_friendly_kernel_param"'"/' /etc/default/grub

# Generate boot loader configuration file
grub-mkconfig -o /boot/grub/grub.cfg

# Enable dhcpcd
systemctl enable dhcpcd

# Install Git
pacman -S --noconfirm git

# Install Ansible
pacman -S --noconfirm python2
pacman -S --noconfirm ansible
