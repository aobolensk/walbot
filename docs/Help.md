**addbgevent**: Add background event  
    Example: !addbgevent 60 hello

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
        !disablecmd hello channel  
        !disablecmd hello guild  
        !disablecmd hello global

**enablecmd**: Enable command in specified scope  
    Examples:  
        !enablecmd hello channel  
        !enablecmd hello guild  
        !enablecmd hello global

**help**: Print list of commands and get examples  
    Examples:  
        !help  
        !help help

**listbgevent**: Print a list of background events  
    Example: !listbgevent

**listreaction**: Show list of reactions  
    Example: !listreaction

**permcmd**: Set commands permission  
    Example: !permcmd hello 0

**permuser**: Set user permission  
    Example: !permcmd @nickname 0

**ping**: Check whether the bot is active  
    Example: !ping

**poll**: Create poll  
    Example: !poll 60 option 1;option 2;option 3

**random**: Get random number in range [left, right]  
    Example: !random 5 10

**updcmd**: Update command (works only for commands that already exist)  
    Example: !updcmd hello Hello!

**version**: Get version of the bot  
    Example: !version

**whitelist**: Bot's whitelist  
    Examples:  
        !whitelist enable/disable  
        !whitelist add  
        !whitelist remove

**wme**: Send direct message to author with something  
    Example: !wme Hello!
