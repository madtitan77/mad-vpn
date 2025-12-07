#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import sys

ADDON = xbmcaddon.Addon('service.mad-vpn')
ADDON_NAME = ADDON.getAddonInfo('name')

def main():
    """Main plugin entry point"""
    dialog = xbmcgui.Dialog()
    dialog.ok(
        ADDON_NAME,
        "MAD VPN Controller is running as a service.\n\n"
        "Use your remote control:\n"
        "RED button - Check VPN status\n"
        "GREEN button - Start VPN\n"
        "YELLOW button - Stop VPN"
    )

if __name__ == '__main__':
    main()
