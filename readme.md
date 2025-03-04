## Work in progress
This project is currently a work in progress. Everything should be functional, but I'm still working on finalizing some details and adding documentation. 

# Description
**Infra_as_Code_Pipelines** is an automated solution for managing infrastructure and Kubernetes deployments using Ansible. This project aims to streamline the process of building and managing both virtual machines and Kubernetes clusters, making it easier to deploy cloud-native applications in self-hosted environments.

#### Key Features
The playbook currently handles the following tasks:

- Kubernetes Cluster Deployment: Automates the creation and configuration of a Kubernetes cluster.
- Calico CNI Installation: Installs and configures the Calico Container Network Interface (CNI) for Kubernetes networking.
- Nginx Ingress Controllers: Installs and configures Nginx as an ingress controller for managing external access to services.
- KVM Server Setup: Installs and configures a KVM (Kernel-based Virtual Machine) server for virtual machine management.
- VM Management: Automates the process of building and deleting virtual machines, offering easy scaling and management.
- CoreDNS Deployment: Installs and configures CoreDNS as a DNS server for the Kubernetes cluster.
- DNS Record Management: Provides functionality for creating, updating, and deleting DNS records to manage domain names within the cluster.

This project is designed to be extendable, with the ability to automate the build and configuration of any type of server. Future enhancements, such as a PostgreSQL pipeline, are planned to further extend its capabilities, making it a flexible solution for a wide variety of infrastructure automation needs.

---

### Usage

### 1. Installing Ansible via pip

You can install Ansible using `pip`, which is a universal method that works across different platforms (Linux, macOS, and Windows). This method requires that you have Python and `pip` installed on your system.

First, ensure that Python and `pip` are installed on your system and then run:
```
pip3 install ansible
```

Alternatively, you can install it with your systems package manager.

### 2. Update Configuration Files
- **[all.yml](inv%2Fgroup_vars%2Fall.yml)**: Update with your SSH key, username, password, and any version changes.
- **[hosts.yaml](inv%2Fhosts.yaml)**: Specify the hostname and IP addresses for your KVM server and any other servers you want to build(e.g., Kubernetes control and worker nodes).
- **[user-data-yml](roles/kvm/templates/user-data.yml.j2)**: Password login is disabled by default. Modify this cloud-init file to enable password login if needed. For more details on cloud-init configuration, refer to the [Cloud-init documentation](https://cloudinit.readthedocs.io/en/latest/reference/index.html).

### 3. KVM Server Prerequisites
Ensure your KVM server meets the following requirements:
- **Root Access**: You must have root access to the server.
- **Resources**: Minimum of 50GB disk space, 12GB RAM, and 4 CPUs (sufficient for a 4-node Kubernetes cluster).
- **CPU Extensions**: Ensure Intel-VT or AMD-V CPU extensions are enabled (required by QEMU).
- **Network Bridge**: A properly configured bridge (br0) is required. While the automation handles the network configuration for all virtual machines created by this project, the network bridge setup is not automated for the KVM server, as there are different ways to configure it based on your environment. This is the only configuration step not managed by the automation.

Below is an example netplan configuration for Ubuntu:

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: false
      dhcp6: false
  bridges:
    br0:
      interfaces:
        - eth0
      addresses:
        - 192.168.1.201/24
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

### 4. DNS
If you build the CoreDNS server before the other servers, the automation will automatically create A records. Alternatively, you can manage DNS resolution manually by editing your local /etc/hosts file.

### 5. Running the Plays
Included below are some examples of arguments you can pass to customize the behavior of the playbooks. For a full list of all available arguments, please refer to the individual playbooks.

1. **Set up the KVM Server**:
   Run the following play to install and configure the KVM server:
   ```bash
   ansible-playbook plays/install_kvm.yaml -i inv/hosts.yaml
   ```
2. **Build CoreDNS Server**
   Run the following play to install and configure the CoreDNS server:
   ```bash
   ansible-playbook plays/build_coredns_server.yaml -i inv/hosts.yaml
   ```
3. **Build Kubernetes Cluster**
   Run the following play to install and configure the Kubernetes cluster. Args to change behavior are in all.yml
   ```bash
   ansible-playbook plays/build_kubernetes_cluster.yaml -i inv/hosts.yaml
   ```
5. **Build Kubernetes Control Plane Server**
  Run the following play to build an control plane node.
   ```
   ansible-playbook plays/build_k8s_control_plane_server.yaml -i inv/hosts.yaml -l <hostname>
   Arguments:
   - --extra-vars "init_master=false": Don't init the control plane to allow manual init. Default(true)
   ```
4. **Build Kubernetes Worker Server**
  Run the following play to build a kubernetes worker.
   ```
   ansible-playbook plays/build_k8s_worker_server.yaml -i inv/hosts.yaml -l <hostname>
   Arguments:
   - --extra-vars "join_cluster=false": Don't join cluster to allow manual join. Default(true)
   ```
5. **Build Ubuntu Server**
   Run the following play to launch an Ubuntu server with nothing installed. It will configure your networking and ssh key.
   ```
   ansible-playbook plays/create_vms.yaml -i inv/hosts.yaml -l <hostname>
   Arguments:
   - --extra-vars "use_backing_file=false": Create a stand alone qcow2 disk image not linked to a backing file. Default(true)
   - --extra-vars "disk_size=20": Allocate 20GB disk image. Default(10)
   - --extra-vars "ram_size=4096": Allocate 4GB of RAM. Default(1024)
   - --extra-vars "cpu_count=4": Allocate 4C CPU's. Default(2)
   ```
6. **Destroy Ubuntu Server**
   Run the following playbook to delete a virtual machine instance.
   ```bash
    ansible-playbook plays/delete_vms.yaml -i inv/hosts.yaml -l <hostname>
    Arguments:
    - --extra-vars "delete_backing_file=true": Deletes the master image if no other VMs are using it. The next VM creation will pull the latest image. (Default: false)
   ```

### 6. Kubernetes

The Nginx ingress controller is installed and configured to handle incoming HTTP/HTTPS traffic on ports 80 and 443 as a NodePort service. To route traffic correctly, ensure it's directed to any node in the cluster, and kube-proxy will forward it to the appropriate backend pod within the cluster. If you prefer not to run a DNS server, a simple alternative is to modify your local /etc/hosts file to resolve the ingress host to the IP address of one of your Kubernetes nodes. For example:

##### Hosts file example:

```bash
192.168.1.202 shortener.dblab.com
```
##### Ingress example:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: url-shortener-ingress
spec:
  ingressClassName: nginx
  rules:
    - host: shortener.dblab.org
      http:
        paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: url-shortener-svc
              port:
                number: 80
```

# Documentation links

- [Kubernetes](https://kubernetes.io/docs/home/)
- [Nginx](https://github.com/kubernetes/ingress-nginx)
- [Calico](https://github.com/projectcalico/calico)
- [Cloud init](https://cloudinit.readthedocs.io/en/latest/reference/index.html)
- [Ansible](https://docs.ansible.com/ansible/latest/index.html)
- [Ubuntu Cloud Images](https://cloud-images.ubuntu.com/)
- [Packer](https://developer.hashicorp.com/packer/integrations/hashicorp/qemu/latest/components/builder/qemu)
- [KVM](https://www.linux-kvm.org/page/Documents)