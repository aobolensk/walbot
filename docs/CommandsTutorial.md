# Commands Tutorial

### How to add new commands to the existing module

1. Create new method inside commands class with name `_<command_name>`.

    Example:
    ```py
    @staticmethod
    async def _test(message, command, silent=False):
    ```
1. Register command in `bind()` function.

    Example:
    ```py
    bc.commands.register_command(__name__, self.get_classname(), "test",
                                 permission=const.Permission.USER.value, subcommand=True)
    ```

### How to add new commands module

1. Create .py file in `src/cmd` directory
1. Create class that is inherited from `BaseCmd` using the following example:

```py
from src.commands import BaseCmd
from src.config import bc


class NewTestCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "test",
                                     permission=const.Permission.USER.value, subcommand=True)

    @staticmethod
    async def _test(message, command, silent=False):
        """Test command"""
        result = "This is the test command!"
        await Msg.response(message, result, silent)
        return result
```

Note: if you want to create private command module you need to create in in `src/cmd/private`. Private commands are fully functional but they are separated from public ones and automatically gitignored.
