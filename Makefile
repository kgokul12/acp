# Makefile to install acp script to /usr/local/bin

SCRIPT_NAME=acp.py
TARGET_NAME=acp
INSTALL_DIR=/usr/local/bin
ACP_DIR=/home/amd/.acp/

install:
	@echo "#Installing $(SCRIPT_NAME) to $(INSTALL_DIR)/$(TARGET_NAME)"
	@sudo cp $(SCRIPT_NAME) $(INSTALL_DIR)/$(TARGET_NAME)
	@sudo chmod +x $(INSTALL_DIR)/$(TARGET_NAME)
	@echo "#Done. Updated you '$(TARGET_NAME)' script."
	@echo "0 8 * * 1 $(ACP_DIR)/update_stable-branch.sh >> $(ACP_DIR)/.log/update_stable-branch.log 1>&2">crontab.sh
	@crontab $(ACP_DIR)/crontab.sh

uninstall:
	@echo "Removing $(INSTALL_DIR)/$(TARGET_NAME)"
	@sudo rm -f $(INSTALL_DIR)/$(TARGET_NAME)
	@echo "Uninstalled."

