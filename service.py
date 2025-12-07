#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import subprocess
import re

ADDON = xbmcaddon.Addon('service.mad-vpn')
ADDON_NAME = ADDON.getAddonInfo('name')


class VPNMonitor(xbmc.Monitor):
    """Monitor for Kodi events"""
    
    def __init__(self):
        xbmc.Monitor.__init__(self)
        self.action_listener = VPNKeyListener()
    
    def onNotification(self, sender, method, data):
        """Handle Kodi notifications"""
        pass


class VPNKeyListener(xbmcgui.WindowXMLDialog):
    """Key listener for remote control"""
    
    def __init__(self):
        # We'll use the Window class to intercept keys
        pass
    
    def onAction(self, action):
        """Handle key press actions"""
        action_id = action.getId()
        
        # Remote color button IDs
        # Red button
        if action_id == 0xF043:  # ACTION_TELETEXT_RED
            xbmc.log("[MAD-VPN] Red button pressed - Checking VPN status", xbmc.LOGINFO)
            self.check_vpn_status()
        # Green button
        elif action_id == 0xF044:  # ACTION_TELETEXT_GREEN
            xbmc.log("[MAD-VPN] Green button pressed - Starting VPN", xbmc.LOGINFO)
            self.start_vpn()
        # Yellow button
        elif action_id == 0xF045:  # ACTION_TELETEXT_YELLOW
            xbmc.log("[MAD-VPN] Yellow button pressed - Stopping VPN", xbmc.LOGINFO)
            self.stop_vpn()
    
    def run_command(self, command):
        """Execute system command and return output"""
        try:
            xbmc.log(f"[MAD-VPN] Executing command: {command}", xbmc.LOGDEBUG)
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            xbmc.log("[MAD-VPN] Command timeout", xbmc.LOGERROR)
            return "Command timed out"
        except Exception as e:
            xbmc.log(f"[MAD-VPN] Command error: {str(e)}", xbmc.LOGERROR)
            return f"Error: {str(e)}"
    
    def parse_vpn_status(self, output):
        """Parse systemctl status output and return status info"""
        status_info = {
            'active': False,
            'running': False,
            'status_text': 'Unknown',
            'icon': xbmcgui.NOTIFICATION_ERROR
        }
        
        # Check for active/inactive
        if 'Active: active (running)' in output:
            status_info['active'] = True
            status_info['running'] = True
            status_info['status_text'] = 'Running'
            status_info['icon'] = xbmcgui.NOTIFICATION_INFO
        elif 'Active: inactive' in output or 'Active: failed' in output:
            status_info['active'] = False
            status_info['running'] = False
            status_info['status_text'] = 'Stopped'
            status_info['icon'] = xbmcgui.NOTIFICATION_WARNING
        elif 'could not be found' in output or 'not found' in output:
            status_info['status_text'] = 'Service Not Found'
            status_info['icon'] = xbmcgui.NOTIFICATION_ERROR
        
        # Extract additional info
        if 'Main PID:' in output:
            match = re.search(r'Main PID: (\d+)', output)
            if match:
                status_info['pid'] = match.group(1)
        
        # Check if enabled
        if 'Loaded:' in output:
            if 'enabled' in output:
                status_info['enabled'] = True
            elif 'disabled' in output:
                status_info['enabled'] = False
        
        return status_info
    
    def check_vpn_status(self):
        """Check OpenVPN service status"""
        output = self.run_command('systemctl status openvpn.service')
        status = self.parse_vpn_status(output)
        
        # Prepare message
        if status['running']:
            message = f"OpenVPN: {status['status_text']}"
            if 'pid' in status:
                message += f"\nPID: {status['pid']}"
        else:
            message = f"OpenVPN: {status['status_text']}"
        
        # Show notification
        xbmcgui.Dialog().notification(
            ADDON_NAME,
            message,
            status['icon'],
            5000  # 5 seconds
        )
        
        xbmc.log(f"[MAD-VPN] Status: {message}", xbmc.LOGINFO)
    
    def start_vpn(self):
        """Start OpenVPN service"""
        xbmcgui.Dialog().notification(
            ADDON_NAME,
            "Starting OpenVPN...",
            xbmcgui.NOTIFICATION_INFO,
            2000
        )
        
        output = self.run_command('systemctl start openvpn.service')
        xbmc.sleep(1000)  # Wait 1 second for service to start
        
        # Check status after starting
        self.check_vpn_status()
    
    def stop_vpn(self):
        """Stop OpenVPN service"""
        xbmcgui.Dialog().notification(
            ADDON_NAME,
            "Stopping OpenVPN...",
            xbmcgui.NOTIFICATION_WARNING,
            2000
        )
        
        output = self.run_command('systemctl stop openvpn.service')
        xbmc.sleep(1000)  # Wait 1 second for service to stop
        
        # Check status after stopping
        self.check_vpn_status()


class ActionHandler(xbmc.Monitor):
    """Main action handler that monitors for key presses"""
    
    def __init__(self):
        xbmc.Monitor.__init__(self)
        self.vpn_listener = VPNKeyListener()
        xbmc.log("[MAD-VPN] Action handler initialized", xbmc.LOGINFO)


def main():
    """Main service loop"""
    xbmc.log("[MAD-VPN] Service starting", xbmc.LOGINFO)
    
    monitor = ActionHandler()
    
    # Create a window to capture actions
    window = xbmcgui.Window(10000)  # Home window
    
    # Keep service running
    while not monitor.abortRequested():
        # Check for key presses
        if xbmc.getCondVisibility('Window.IsActive(home)') or True:
            # Get the current window
            current_window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            
            # Check for action using xbmc.getInfoLabel
            action_id = xbmc.getInfoLabel('System.CurrentControl')
        
        # Sleep for a bit
        if monitor.waitForAbort(0.1):
            break
    
    xbmc.log("[MAD-VPN] Service stopped", xbmc.LOGINFO)


if __name__ == '__main__':
    main()
