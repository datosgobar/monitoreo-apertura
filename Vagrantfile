VAGRANTFILE_API_VERSION = "2"

SSH_KEYS = [ '~/.vagrant.d/insecure_private_key', '~/.ssh/id_rsa']


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "bento/ubuntu-16.04"
  config.ssh.private_key_path = SSH_KEYS
  config.ssh.forward_agent = true
  config.ssh.insert_key = false
  config.vm.define "webserver" do |web|
      web.ssh.private_key_path = SSH_KEYS
      web.ssh.forward_agent = true
      web.ssh.insert_key = false
      web.vm.network "private_network", ip: "192.168.33.10"
  end
  config.vm.provision "ansible" do |ansible|
    ansible.compatibility_mode = "2.0"
    ansible.playbook = "deploy/site.yml"
    ansible.inventory_path = "deploy/inventories/vagrant/hosts"
    ansible.limit = "all"
    ansible.verbose = "vvv"
  end
end
