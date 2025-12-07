#!/bin/bash

# MAD VPN Controller - Deployment Script
# This script deploys the addon to a remote Kodi instance via SSH

set -e  # Exit on error

# Configuration
REMOTE_HOST="kodi"
ADDON_ID="service.mad-vpn"
KODI_ADDONS_DIR="/storage/.kodi/addons"
KODI_KEYMAPS_DIR="/storage/.kodi/userdata/keymaps"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================"
echo "MAD VPN Controller - Deployment Script"
echo "======================================"
echo ""
echo "Remote host: $REMOTE_HOST"
echo "Local directory: $LOCAL_DIR"
echo ""

# Test SSH connection
echo "Testing SSH connection to $REMOTE_HOST..."
if ! ssh -q -o ConnectTimeout=5 "$REMOTE_HOST" exit; then
    echo "ERROR: Cannot connect to $REMOTE_HOST via SSH"
    echo "Please check:"
    echo "  1. SSH is configured in ~/.ssh/config or use user@host format"
    echo "  2. SSH keys are set up"
    echo "  3. Host is reachable"
    exit 1
fi
echo "✓ SSH connection successful"
echo ""

# Create remote directories if they don't exist
echo "Creating remote directories..."
ssh "$REMOTE_HOST" "mkdir -p $KODI_ADDONS_DIR/$ADDON_ID"
ssh "$REMOTE_HOST" "mkdir -p $KODI_KEYMAPS_DIR"
echo "✓ Remote directories ready"
echo ""

# Copy addon files
echo "Copying addon files..."
scp -q "$LOCAL_DIR/addon.xml" "$REMOTE_HOST:$KODI_ADDONS_DIR/$ADDON_ID/"
scp -q "$LOCAL_DIR/default.py" "$REMOTE_HOST:$KODI_ADDONS_DIR/$ADDON_ID/"
scp -q "$LOCAL_DIR/service.py" "$REMOTE_HOST:$KODI_ADDONS_DIR/$ADDON_ID/"
scp -q "$LOCAL_DIR/keyhandler.py" "$REMOTE_HOST:$KODI_ADDONS_DIR/$ADDON_ID/"
scp -q "$LOCAL_DIR/settings.xml" "$REMOTE_HOST:$KODI_ADDONS_DIR/$ADDON_ID/"
echo "✓ Addon files copied"
echo ""

# Copy language files if they exist
if [ -d "$LOCAL_DIR/resources" ]; then
    echo "Copying language resources..."
    ssh "$REMOTE_HOST" "mkdir -p $KODI_ADDONS_DIR/$ADDON_ID/resources/language/resource.language.en_gb"
    scp -q "$LOCAL_DIR/resources/language/resource.language.en_gb/strings.po" \
        "$REMOTE_HOST:$KODI_ADDONS_DIR/$ADDON_ID/resources/language/resource.language.en_gb/"
    echo "✓ Language resources copied"
    echo ""
fi

# Copy keymap
echo "Copying keymap configuration..."
scp -q "$LOCAL_DIR/keymap.xml" "$REMOTE_HOST:$KODI_KEYMAPS_DIR/mad-vpn.xml"
echo "✓ Keymap installed"
echo ""

# Set executable permissions
echo "Setting permissions..."
ssh "$REMOTE_HOST" "chmod +x $KODI_ADDONS_DIR/$ADDON_ID/*.py"
echo "✓ Permissions set"
echo ""

# Check if Kodi is running
echo "Checking Kodi status..."
if ssh "$REMOTE_HOST" "pgrep -x kodi > /dev/null"; then
    echo "⚠ Kodi is currently running"
    echo ""
    read -p "Do you want to restart Kodi to load the addon? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Restarting Kodi..."
        ssh "$REMOTE_HOST" "systemctl restart kodi" || echo "Note: If restart failed, you may need to restart manually"
        echo "✓ Kodi restart initiated"
    else
        echo "⚠ Please restart Kodi manually or reload keymaps from Kodi settings"
    fi
else
    echo "✓ Kodi is not running (will load addon on next start)"
fi

echo ""
echo "======================================"
echo "✓ Deployment completed successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Start Kodi if not running"
echo "  2. Go to Settings → Addons → My Addons → Services"
echo "  3. Enable 'MAD VPN Controller'"
echo "  4. Test with remote buttons:"
echo "     - RED: Check VPN status"
echo "     - GREEN: Start VPN"
echo "     - YELLOW: Stop VPN"
echo ""
echo "  Or test with keyboard: F1 (status), F2 (start), F3 (stop)"
echo ""
