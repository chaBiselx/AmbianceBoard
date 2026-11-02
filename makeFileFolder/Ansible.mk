ANSIBLE_CONFIG=infra/ansible/ansible.cfg

## —— Ansible ————————————————————————————————————————————————————————————————
ansible-check: ansible-check-setup
	@# Help: Vérifie la configuration d'Ansible pour l'ensemble des playbooks


ansible-check-setup:
	@# Help: Vérifie la configuration d'Ansible pour le playbook setup.yml
	ANSIBLE_CONFIG=$(ANSIBLE_CONFIG) ansible-playbook -i localhost, --syntax-check ansible/playbooks/setup.yml

ansible-update:
	@# Help: Met à jour les dependances du serveur et fait les installations si besoin
	ANSIBLE_CONFIG=$(ANSIBLE_CONFIG) ansible-playbook ./playbooks/setup.yml