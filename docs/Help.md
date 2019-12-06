**addalias**: Add alias for commands  
    Usage: !addalias <command> <alias>  
    Example: !addalias ping pong

**addbgevent**: Add background event  
    Example: !addbgevent 60 ping

**addcmd**: Add command  
    Example: !addcmd hello Hello!

**addimg**: Add image for !img command  
    Example: !addimg name url

**addreaction**: Add reaction  
    Example: !addreaction emoji regex

**avatar**: Change bot avatar  
    Example: !avatar <image>  
    Hint: Use !listimg for list of available images

**channelid**: Get channel ID  
    Example: !channelid  
    *This command can be used as subcommand*

**delalias**: Delete command alias  
    Usage: !delalias <alias>  
    Example: !delalias pong

**delbgevent**: Delete background event  
    Example: !delbgevent 0

**delcmd**: Delete command  
    Example: !delcmd hello

**delimg**: Delete image for !img command  
    Example: !delimg name

**delmarkov**: Delete all words in Markov model by regex  
    Example: !delmarkov hello

**delreaction**: Delete reaction  
    Examples:  
        !delreaction emoji  
        !delreaction index

**demojify**: Demojify text  
    Example: !demojify 🇭 🇪 🇱 🇱 🇴  
    *This command can be used as subcommand*

**disablecmd**: Disable command in specified scope  
    Examples:  
        !disablecmd ping channel  
        !disablecmd ping guild  
        !disablecmd ping global

**emojify**: Emojify text  
    Example: !emojify Hello!  
    *This command can be used as subcommand*

**enablecmd**: Enable command in specified scope  
    Examples:  
        !enablecmd ping channel  
        !enablecmd ping guild  
        !enablecmd ping global

**forchannel**: Executes command for channel  
    Example: !forchannel <channel_id> ping

**help**: Print list of commands and get examples  
    Examples:  
        !help  
        !help help

**img**: Send image (use !listimg for list of available images)  
    Example: !img

**listalias**: Show list of aliases  
    Example: !listalias

**listbgevent**: Print a list of background events  
    Example: !listbgevent

**listimg**: List of available images for !img command  
    Example: !listimg

**listreaction**: Show list of reactions  
    Example: !listreaction

**markov**: Generate message using Markov chain  
    Example: !markov  
    *This command can be used as subcommand*

**markovlog**: Enable/disable adding messages from this channel to Markov model  
    Examples:  
        !markovlog  
        !markovlog enable  
        !markovlog disable

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
    *This command can be used as subcommand*

**reactionwl**: Add/delete channel from reaction whitelist  
    Examples:  
        !reactionwl  
        !reactionwl add  
        !reactionwl delete

**shutdown**: Shutdown the bot  
    Example: !shutdown

**silent**: Make the following command silent (without any output to the chat)  
    Example: !silent ping

**status**: Change bot status  
    Example: !status playing Dota 2  
    Possible activities: [playing, streaming, watching, listening]

**time**: Show current time and bot deployment time  
    Example: !time  
    *This command can be used as subcommand*

**timescmd**: Print how many times command was invoked  
    Example: !timescmd echo

**tts**: Send text-to-speech (TTS) message  
    Example: !tts Hello!

**updcmd**: Update command (works only for commands that already exist)  
    Example: !updcmd hello Hello!

**updreaction**: Update reaction  
    Example: !updreaction index emoji regex

**uptime**: Show bot uptime  
    Example: !uptime  
    *This command can be used as subcommand*

**urlencode**: Urlencode string  
    Example: !urlencode hello, world!  
    *This command can be used as subcommand*

**version**: Get version of the bot  
    Example: !version  
    *This command can be used as subcommand*

**whitelist**: Bot's whitelist  
    Examples:  
        !whitelist enable/disable  
        !whitelist add  
        !whitelist remove

**wme**: Send direct message to author with something  
    Example: !wme Hello!
