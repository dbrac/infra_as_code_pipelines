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

This project is designed to be extendable, with the ability to automate the build and configuration of any type of server. Future enhancements, such as a PostgreSQL "pipeline," are planned to further extend its capabilities, making it a flexible solution for a wide variety of infrastructure automation needs.

---

## Usage

### 1. Update Configuration Files
- **[all.yml](inv%2Fgroup_vars%2Fall.yml)**: Update with your SSH key, username, password, and any version changes.
- **[hosts.yaml](inv%2Fhosts.yaml)**: Specify the hostname and IP addresses for your KVM server and any other servers you want to build(e.g., Kubernetes control and worker nodes).
- **[user-data-yml](roles/kvm/templates/user-data.yml.j2)**: Password login is disabled by default. Modify this cloud-init file to enable password login if needed. For more details on cloud-init configuration, refer to the [Cloud-init documentation](https://cloudinit.readthedocs.io/en/latest/reference/index.html).

### 2. KVM Server Prerequisites
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

### 3. DNS
If you build the CoreDNS server before the other servers, the automation will automatically create A records. Alternatively, you can manage DNS resolution manually by editing your local /etc/hosts file.

### 4. Running the Plays

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
   Run the following play to install and configure the Kubernetes cluster:
   ```bash
   ansible-playbook plays/build_kubernetes_cluster.yaml -i inv/hosts.yaml
   ```
4. **Build Kubernetes Worker**
   ```
   ansible-playbook plays/build_k8s_worker_server.yaml -i inv/hosts.yaml
   ```
5. **Build Ubuntu Server**
   ```
   Run the following play to launch an Ubuntu server with nothing installed. It will configure your networking and ssh key.
   ansible-playbook plays/create_vms.yaml -i inv/hosts.yaml
   ```
6. **Destroy Ubuntu Server**
   ```bash
      ansible-playbook plays/delete_vms.yaml -i inv/hosts.yaml
   ```

## 5. Kubernetes

The Nginx ingress controller is installed and configured to handle incoming HTTP/HTTPS traffic on 80 and 443 as a node port service. You just need to ensure your traffic is routed correctly to any node in the cluster and it will get routed over the pod network to nginx. If you don't want to run a DNS server, a simple method is to modify your local /etc/hosts file to resolve the ingress host to the IP of your Kubernetes node. For example:

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