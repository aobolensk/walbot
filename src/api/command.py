class BaseCmd:
    @classmethod
    def get_classname(cls) -> str:
        return cls.__name__

    def bind(self) -> None:
        raise NotImplementedError(f"Class {self.get_classname()} does not have bind() function")
