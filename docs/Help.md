**addbgevent**: Add background event  
    Example: !addbgevent 60 ping

**addcmd**: Add command  
    Example: !addcmd hello Hello!

**addreaction**: Add reaction  
    Example: !addreaction emoji regex

**delbgevent**: Delete background event  
    Example: !delbgevent 0

**delcmd**: Delete command  
    Example: !delcmd hello

**delreaction**: Delete reaction  
    Example: !delreaction emoji

**disablecmd**: Disable command in specified scope  
    Examples:  
        !disablecmd ping channel  
        !disablecmd ping guild  
        !disablecmd ping global

**enablecmd**: Enable command in specified scope  
    Examples:  
        !enablecmd ping channel  
        !enablecmd ping guild  
        !enablecmd ping global

**help**: Print list of commands and get examples  
    Examples:  
        !help  
        !help help

**listbgevent**: Print a list of background events  
    Example: !listbgevent

**listreaction**: Show list of reactions  
    Example: !listreaction

**permcmd**: Set commands permission  
    Example: !permcmd ping 0

**permuser**: Set user permission  
    Example: !permcmd @nickname 0

**ping**: Check whether the bot is active  
    Example: !ping

**poll**: Create poll  
    Example: !poll 60 option 1;option 2;option 3

**random**: Get random number in range [left, right]  
    Example: !random 5 10

**silent**: Make the following command silent (without any output to the chat)  
    Example: !silent ping

**status**: Change bot status  
    Example: !status playing Dota 2  
    Possible activities: [playing, streaming, watching, listening]

**time**: Show current time and bot deployment time  
    Example: !time

**updcmd**: Update command (works only for commands that already exist)  
    Example: !updcmd hello Hello!

**uptime**: Show bot uptime  
    Example: !uptime

**version**: Get version of the bot  
    Example: !version

**whitelist**: Bot's whitelist  
    Examples:  
        !whitelist enable/disable  
        !whitelist add  
        !whitelist remove

**wme**: Send direct message to author with something  
    Example: !wme Hello!
