#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import subprocess
import re
import sys

# Explicitly specify the addon ID when running from keymap
ADDON = xbmcaddon.Addon('service.mad-vpn')
ADDON_NAME = ADDON.getAddonInfo('name')


def run_command(command):
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


def parse_vpn_status(output):
    """Parse systemctl status output and return status info"""
    status_info = {
        'active': False,
        'running': False,
        'status_text': 'Unknown',
        'icon': xbmcgui.NOTIFICATION_ERROR
    }
    
    # Log output length for debugging
    xbmc.log(f"[MAD-VPN] Parsing output length: {len(output)}", xbmc.LOGDEBUG)
    
    # Check for active/inactive
    if 'Active: active (running)' in output or 'active (running)' in output:
        status_info['active'] = True
        status_info['running'] = True
        status_info['status_text'] = 'Running'
        status_info['icon'] = xbmcgui.NOTIFICATION_INFO
    elif 'Active: inactive' in output or 'inactive (dead)' in output:
        status_info['active'] = False
        status_info['running'] = False
        status_info['status_text'] = 'Stopped'
        status_info['icon'] = xbmcgui.NOTIFICATION_WARNING
    elif 'Active: failed' in output or 'failed' in output:
        status_info['active'] = False
        status_info['running'] = False
        status_info['status_text'] = 'Failed'
        status_info['icon'] = xbmcgui.NOTIFICATION_ERROR
    elif 'could not be found' in output or 'not found' in output or 'not-found' in output:
        status_info['status_text'] = 'Service Not Found'
        status_info['icon'] = xbmcgui.NOTIFICATION_ERROR
    elif 'loaded' in output.lower() and 'active' in output.lower():
        # Fallback check
        status_info['status_text'] = 'Active (check logs)'
        status_info['icon'] = xbmcgui.NOTIFICATION_INFO
    
    # Extract additional info
    if 'Main PID:' in output:
        match = re.search(r'Main PID: (\d+)', output)
        if match:
            status_info['pid'] = match.group(1)
    
    return status_info


def check_vpn_status():
    """Check OpenVPN service status"""
    output = run_command('systemctl status openvpn.service')
    
    # Log the raw output for debugging
    xbmc.log(f"[MAD-VPN] Raw systemctl output: {output[:500]}", xbmc.LOGDEBUG)
    
    status = parse_vpn_status(output)
    
    # Prepare message
    if status['running']:
        message = f"OpenVPN: {status['status_text']}"
        if 'pid' in status:
            message += f" (PID: {status['pid']})"
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


def start_vpn():
    """Start OpenVPN service"""
    xbmcgui.Dialog().notification(
        ADDON_NAME,
        "Starting OpenVPN...",
        xbmcgui.NOTIFICATION_INFO,
        2000
    )
    
    output = run_command('systemctl start openvpn.service')
    xbmc.sleep(1000)  # Wait 1 second for service to start
    
    # Check status after starting
    check_vpn_status()


def stop_vpn():
    """Stop OpenVPN service"""
    xbmcgui.Dialog().notification(
        ADDON_NAME,
        "Stopping OpenVPN...",
        xbmcgui.NOTIFICATION_WARNING,
        2000
    )
    
    output = run_command('systemctl stop openvpn.service')
    xbmc.sleep(1000)  # Wait 1 second for service to stop
    
    # Check status after stopping
    check_vpn_status()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        action = sys.argv[1]
        xbmc.log(f"[MAD-VPN] Key handler called with action: {action}", xbmc.LOGINFO)
        
        if action == 'status':
            check_vpn_status()
        elif action == 'start':
            start_vpn()
        elif action == 'stop':
            stop_vpn()
        else:
            xbmc.log(f"[MAD-VPN] Unknown action: {action}", xbmc.LOGWARNING)
    else:
        xbmc.log("[MAD-VPN] No action specified", xbmc.LOGWARNING)


if __name__ == '__main__':
    main()
