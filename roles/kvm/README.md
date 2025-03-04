# KVM VM Management Role Documentation

## Overview

This Ansible role automates the installation and management of KVM-based virtual machines. It handles tasks like installing necessary packages, checking CPU virtualization support, managing VM creation and deletion, and cleaning up VM files. KVM install should work on any debian based system. The VM creation will produce ubuntu VM's.

## Key Tasks
1. **Install and Configure KVM**: 
   - Installs necessary KVM packages.
   - Verifies if CPU virtualization extensions are enabled.

2. **VM Creation**:
   - Downloads a cloud image (if not present).
   - Creates a new VM with specified resources (CPU, RAM, disk).
   - Configures networking and cloud-init.

3. **VM Deletion**:
   - Stops and undefines the VM.
   - Deletes the VM image and related files.
   - Optionally deletes the base image if no VMs are using it.

4. **Directory Management**:
   - Creates required directories for VM images and configurations.

## Usage
- **VM Creation**: To create a new VM, the role ensures the necessary resources are available, downloads the cloud image, and sets up the VM with specified configurations. Defaults to building "linked clones" with a backing file. Optionally, it can build stand alone vm disk images. 
- **VM Deletion**: Cleans up by stopping and removing the VM, as well as cleaning the image files. Optionally, it can delete the master base image if no other VM's are using it to facilitate updating the image.

## TODO
- Add support for creating multiple users and ssh keys
- Add support for creating other OS distribution