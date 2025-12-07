# MAD VPN Controller - Kodi Addon

A Kodi addon to control OpenVPN service using remote control colored buttons.

## Features

- **RED button**: Check VPN status
- **GREEN button**: Start VPN service
- **YELLOW button**: Stop VPN service

## Installation

1. Copy the entire `service.mad-vpn` folder to your Kodi addons directory:
   - Linux: `~/.kodi/addons/`
   - Windows: `%APPDATA%\Kodi\addons\`
   - Android: `/storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi/addons/`

2. Rename the folder from `mad-vpn` to `service.mad-vpn`

3. Install the keymap:
   ```bash
   mkdir -p ~/.kodi/userdata/keymaps/
   cp keymap.xml ~/.kodi/userdata/keymaps/mad-vpn.xml
   ```

4. Restart Kodi or reload keymaps from Settings → System → Input → Reload Keymaps

5. Enable the addon in Kodi:
   - Go to Settings → Addons → My Addons → Services
   - Enable "MAD VPN Controller"

## Requirements

- Kodi 19 (Matrix) or later
- Python 3.x
- systemctl access (Linux systems)
- Proper permissions to control systemd services (may require sudoers configuration)

## Permissions Setup

The addon needs permission to run systemctl commands.

**Check if Kodi is running as root:**
```bash
ps aux | grep kodi
```

If Kodi is running as root (first column shows "root"), you don't need any additional permissions setup. The addon will work out of the box.

**If Kodi is running as a regular user (e.g., 'kodi'):**

Create a sudoers file to allow the Kodi user to control OpenVPN without password:
```bash
sudo visudo -f /etc/sudoers.d/kodi-vpn
```

Add these lines (replace `kodi` with your actual Kodi user):
```
kodi ALL=(ALL) NOPASSWD: /bin/systemctl status openvpn.service
kodi ALL=(ALL) NOPASSWD: /bin/systemctl start openvpn.service
kodi ALL=(ALL) NOPASSWD: /bin/systemctl stop openvpn.service
```

Then update the keyhandler.py commands to use sudo:
- Change `systemctl` to `sudo systemctl` in all three command calls

## Testing

You can test the addon using keyboard keys:
- **F1**: Check status (same as RED button)
- **F2**: Start VPN (same as GREEN button)
- **F3**: Stop VPN (same as YELLOW button)

## Troubleshooting

1. **Addon not responding to button presses**:
   - Check Kodi log: `~/.kodi/temp/kodi.log`
   - Look for `[MAD-VPN]` entries
   - Make sure keymap is properly installed

2. **Permission denied errors**:
   - Configure sudoers as described above
   - Check that the Kodi user has proper permissions

3. **Service not found**:
   - Verify OpenVPN is installed: `systemctl status openvpn.service`
   - You may need to adjust the service name (e.g., `openvpn@client.service`)

## Customization

To change the service name or commands, edit `keyhandler.py` and modify the `run_command()` calls.

## License

GPL-2.0-or-later
