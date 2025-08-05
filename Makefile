# Makefile to install acp script to /usr/local/bin

SCRIPT_NAME=acp.py
TARGET_NAME=acp
INSTALL_DIR=/usr/local/bin

install:
	@echo "#Installing $(SCRIPT_NAME) to $(INSTALL_DIR)/$(TARGET_NAME)"
	@sudo cp $(SCRIPT_NAME) $(INSTALL_DIR)/$(TARGET_NAME)
	@sudo chmod +x $(INSTALL_DIR)/$(TARGET_NAME)
	@echo "#Done. Updated you '$(TARGET_NAME)' script."

uninstall:
	@echo "Removing $(INSTALL_DIR)/$(TARGET_NAME)"
	@sudo rm -f $(INSTALL_DIR)/$(TARGET_NAME)
	@echo "Uninstalled."

